import os
import asyncio
import datetime
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from agent.agentic_workflow import GraphBuilder
from utils.save_to_document import save_document

# Optional: direct LLM access for streaming
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
import uvicorn

load_dotenv()

app = FastAPI()

# Allow frontend apps (Streamlit, React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ⚠️ In prod, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


# ---- Non-streaming JSON endpoint ----
@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        graph = GraphBuilder(model_provider="groq")
        react_app = graph()

        async def run_invoke():
            messages = {"messages": [query.question]}
            return react_app.invoke(messages)

        # Timeout after 50s (Render kills after 60s)
        output = await asyncio.wait_for(run_invoke(), timeout=50)

        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)

        return {"answer": final_output}

    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"error": "Request timed out, try again with a shorter query."},
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ---- Streaming endpoint (best for frontends like Streamlit) ----
groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",  # ✅ fast & cheap model
    api_key=groq_api_key,
    streaming=True,
)

@app.get("/chat")
async def chat(query: str):
    async def event_generator():
        async for chunk in llm.astream([HumanMessage(content=query)]):
            if chunk.content:
                yield chunk.content

    return StreamingResponse(event_generator(), media_type="text/plain")


# ---- Root healthcheck ----
@app.get("/")
async def root():
    return {"status": "ok", "time": datetime.datetime.now().isoformat()}


# ---- Entry point for local dev ----
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Render injects $PORT
    uvicorn.run(app, host="0.0.0.0", port=port)
