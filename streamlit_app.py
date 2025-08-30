import streamlit as st
import requests
import datetime

# Backend endpoint on Render
BASE_URL = "https://ai-trip-planner-2-qdl4.onrender.com"

# Page configuration
st.set_page_config(
    page_title="🌍 Chethan AI Travel Planner",
    page_icon="🌍",
    layout="wide",
)

# Custom CSS for chat bubbles
st.markdown(
    """
    <style>
    .user-bubble {
        background-color: #DCF8C6;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    .bot-bubble {
        background-color: #F1F0F0;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    .timestamp {
        font-size: 0.8em;
        color: gray;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar info
with st.sidebar:
    st.markdown("## 🌍 AI Travel Planner")
    st.write(
        """
        🧳 Your personal **AI-powered Travel Agent**.  
        Type in your trip request, e.g.  
        *Plan a 3-day trip to Coorg for 2 people under ₹10,000*.  
        
        ✨ The AI will generate a full itinerary.  
        """
    )
    st.markdown("---")
    st.caption("Built with ❤️ by Chethan's Travel Agent")

st.title("🌍 Travel Planner Agentic Application")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history (chat-like format)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{msg['content']}</div>", unsafe_allow_html=True)

# Input at the bottom
st.markdown("## 💬 Ask me about your trip")
user_input = st.chat_input("e.g. Plan a trip to Goa for 5 days")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='user-bubble'>{user_input}</div>", unsafe_allow_html=True)

    try:
        with st.spinner("🤖 Bot is preparing your travel plan..."):
            payload = {"question": user_input}
            response = requests.post(f"{BASE_URL}/query", json=payload, timeout=60)

        if response.status_code == 200:
            answer = response.json().get("answer", "⚠️ No answer returned.")
            plan = f"""
**🗓 Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  
**✍️ Created by:** Chethan's Travel Agent  

---

{answer}

---

*🔎 Please verify all details (prices, hours, requirements) before your trip.*
"""
            st.session_state.messages.append({"role": "bot", "content": plan})
            st.markdown(f"<div class='bot-bubble'>{plan}</div>", unsafe_allow_html=True)

        else:
            error_msg = f"❌ Bot failed to respond: {response.text}"
            st.session_state.messages.append({"role": "bot", "content": error_msg})
            st.error(error_msg)

    except requests.exceptions.Timeout:
        st.error("⚠️ Request timed out. Please try again later.")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Could not connect to backend. Please check if the API is live.")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {e}")
