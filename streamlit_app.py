import streamlit as st
import requests
import datetime

# Backend endpoint on Render
BASE_URL = "https://ai-trip-planner-2-qdl4.onrender.com"

# Streamlit page configuration
st.set_page_config(
    page_title="🌍 Travel Planner Agentic Application",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar info
with st.sidebar:
    st.header("ℹ️ About")
    st.write(
        """
        Welcome to **Chethan's AI Travel Planner** ✈️🌍  
        
        👉 Enter your trip query (e.g., *Plan a 5-day trip to Goa for 3 people under ₹20,000*).  
        The AI will generate a customized itinerary.  

        You can submit multiple queries — results are saved in history.
        """
    )
    st.markdown("---")
    st.caption("🚀 Built with Streamlit + FastAPI")

# Main title
st.title("🌍 AI Travel Planner")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous travel plans
if st.session_state.messages:
    st.subheader("📜 Previous Plans")
    for idx, msg in enumerate(st.session_state.messages):
        st.markdown(msg, unsafe_allow_html=True)
        st.markdown("---")

# Input form
st.subheader("💬 Tell me about your trip")
with st.form(key="query_form", clear_on_submit=True):
    user_input = st.text_input("Your Query", placeholder="e.g. Plan a trip to Coorg for 4 days under ₹15,000")
    submit_button = st.form_submit_button("Generate Plan")

# Handle query
if submit_button and user_input.strip():
    try:
        with st.spinner("🤖 Thinking... Generating your travel plan..."):
            payload = {"question": user_input}
            response = requests.post(f"{BASE_URL}/query", json=payload, timeout=60)

        if response.status_code == 200:
            answer = response.json().get("answer", "⚠️ No answer returned.")
            markdown_content = f"""
# 🌍 AI Travel Plan  

**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Created by:** Chethan's Travel Agent  

---

{answer}

---

*🔎 Please verify prices, timings, and requirements before booking.*
"""
            st.success("✅ Travel plan generated!")
            st.markdown(markdown_content)
            # Save to history
            st.session_state.messages.append(markdown_content)
        else:
            st.error(f"❌ Bot failed to respond. Status: {response.status_code}\n\n{response.text}")

    except requests.exceptions.Timeout:
        st.error("⚠️ The request timed out. Please try again later.")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Could not connect to backend. Please check if the API is live.")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {e}")
