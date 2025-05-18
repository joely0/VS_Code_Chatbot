import os
import streamlit as st
from openai import OpenAI
import importlib.metadata

# --- OpenAI Setup ---
openai_version = importlib.metadata.version("openai")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
available_models = ["gpt-3.5-turbo", "gpt-4"]

# --- Sidebar ---
st.sidebar.title("⚙️ Settings")
selected_model = st.sidebar.selectbox("Choose a model", available_models)
st.sidebar.markdown(f"📦 **OpenAI SDK:** `{openai_version}`")
st.sidebar.markdown(f"🧠 **Model in use:** `{selected_model}`")
st.sidebar.markdown("---")
st.sidebar.markdown("ℹ️ Token tracking disabled in streaming mode.")

# --- App Title ---
st.title("💬 ChatGPT Assistant")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

# --- Display Message History ---
for msg in st.session_state.messages[1:]:  # skip system prompt
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input Handling Function ---
def submit_input(prompt):
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream assistant response
    try:
        with st.chat_message("assistant"):
            full_response = ""
            stream = client.chat.completions.create(
                model=selected_model,
                messages=st.session_state.messages,
                stream=True
            )
            placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        st.stop()

# --- Chat Input (Pinned to Bottom) ---
if prompt := st.chat_input("You:"):
    submit_input(prompt)
