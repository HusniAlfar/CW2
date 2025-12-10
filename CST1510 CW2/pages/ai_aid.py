import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# We load variables from .env file (this keeps secrets outside code)
load_dotenv(override=True)

# Read the OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create OpenAI client
# If the key is in the env, the client can talk to the API
client = OpenAI(api_key=OPENAI_API_KEY)

# Import our data helpers from the H.I.V.E. database
from hive_database.data_loader import (
    load_cyber_incidents,
    load_datasets_metadata,
    load_it_tickets,
)

# ============================
# Page configuration
# ============================
st.set_page_config(
    page_title='H.I.V.E AI Assistant "JARVIS"',
    page_icon="🤖",
    layout="wide",
)

# ============================
# Check login status
# ============================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please login first to access H.I.V.E. AI.")
    st.stop()

# ============================
# Sidebar navigation
# ============================
st.sidebar.title("H.I.V.E. Navigation")
st.sidebar.markdown("---")
st.sidebar.write(f"**Agent:** {st.session_state.username}")
st.sidebar.write(f"**Role:** {st.session_state.role}")
st.sidebar.markdown("---")

# Link back to main H.I.V.E. dashboard
st.sidebar.page_link("pages/dash.py", label=" H.I.V.E. Home Page",)

st.sidebar.markdown("---")

# Logout button
if st.sidebar.button(" Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# ============================
# Main content
# ============================
st.title(' JARVIS – H.I.V.E. AI Assistant')
st.markdown("### Ask questions about your H.I.V.E. data")
st.markdown("---")

# We keep the chat messages in session state
# so they stay on the page after each rerun
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def get_data_context() -> str:
    """
    Make a short text summary of all three domains.
    This text will be sent to OpenAI as context.
    """
    context = "Here is the current data from the H.I.V.E. platform:\n\n"

    # --- Cybersecurity data ---
    cyber_df = load_cyber_incidents()
    context += "CYBERSECURITY:\n"
    context += f"- Total incidents: {len(cyber_df)}\n"
    context += f"- Open incidents: {len(cyber_df[cyber_df['status'] == 'Open'])}\n"
    context += f"- Critical incidents: {len(cyber_df[cyber_df['severity'] == 'Critical'])}\n"
    context += f"- Phishing incidents: {len(cyber_df[cyber_df['category'] == 'Phishing'])}\n\n"

    # --- Dataset data ---
    datasets_df = load_datasets_metadata()
    context += "DATASETS:\n"
    context += f"- Total datasets: {len(datasets_df)}\n"
    context += f"- Total rows across all datasets: {datasets_df['rows'].sum()}\n\n"

    # --- IT tickets data ---
    tickets_df = load_it_tickets()
    context += "IT TICKETS:\n"
    context += f"- Total tickets: {len(tickets_df)}\n"
    context += f"- Open tickets: {len(tickets_df[tickets_df['status'] == 'Open'])}\n"
    context += (
        f"- Average resolution time: "
        f"{tickets_df['resolution_time_hours'].mean():.1f} hours\n"
    )

    return context


def get_ai_response(user_message: str) -> str:
    """
    Send a question and the data context to OpenAI.
    Return the answer text from the model.
    """
    # If the key is missing, we tell the user
    if not OPENAI_API_KEY:
        return "AI is not configured. Please set OPENAI_API_KEY in your .env file."

    try:
        # Build context about the data
        data_context = get_data_context()

        # This is the final prompt we send to the model
        full_prompt = (
            f"{data_context}\n\n"
            f"User question: {user_message}\n\n"
            "You are JARVIS, the H.I.V.E. AI assistant. "
            "Explain in clear and simple English. "
            "Give short explanations and 2–3 practical suggestions."
        )

        # Call OpenAI Chat Completions API
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, an AI assistant for the H.I.V.E. platform. "
                        "You help agents understand cybersecurity, data science, "
                        "and IT operations data."
                    ),
                },
                {"role": "user", "content": full_prompt},
            ],
        )

        # Get the text from the first choice
        return response.choices[0].message.content

    except Exception as e:
        # If there is any error, we return it as text
        return f"Error from AI: {e}"


# ============================
# Show chat history
# ============================
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

# ============================
# Chat input box
# ============================
user_input = st.chat_input("Ask JARVIS anything about your H.I.V.E. data...")

if user_input:
    # Save and show user message
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.write(user_input)

    # Ask OpenAI for an answer
    with st.chat_message("assistant"):
        with st.spinner("JARVIS is thinking..."):
            ai_reply = get_ai_response(user_input)
            st.write(ai_reply)

    # Save AI answer
    st.session_state.chat_history.append(
        {"role": "assistant", "content": ai_reply}
    )

    # Rerun page to update the full chat display
    st.rerun()

# Button to clear chat
if st.button("🧹 Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

st.markdown("---")
st.caption(" JARVIS – H.I.V.E. AI Assistant Module")
