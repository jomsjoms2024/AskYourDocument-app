import streamlit as st
from typing import Generator
from groq import Groq

st.set_page_config(page_icon="🌐", layout="wide", page_title="ChatAPP")


def icon(emoji: str):
    """Displays an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

icon("⌨️")

st.subheader("Chat_App")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Define model details
models = {
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
    "llama2-70b-4096": {"name": "LLaMA2-70b-chat", "tokens": 4096, "developer": "Meta"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
}

# Filter out only LLaMA models
llama_models = {k: v for k, v in models.items() if 'llama3' in k.lower()}

# Layout for model selection and clear chat button
with st.container():
    st.write("#### Model Selection")
    col1, col2 = st.columns([4, 1])

    with col1:
        model_option = st.selectbox(
            "Choose a model:",
            options=list(llama_models.keys()),
            format_func=lambda x: llama_models[x]["name"],
            index=0
        )

    with col2:
        if st.button("Clear Chat"):
            st.session_state.messages = []

    if st.session_state.selected_model != model_option:
        st.session_state.messages = []
        st.session_state.selected_model = model_option

# Display chat messages from history
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
    with st.container():
        st.markdown(f'<div class="chat-message {message["role"]}">{message["content"]}</div>', unsafe_allow_html=True)

def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.container():
        st.markdown(f'<div class="chat-message user">{prompt}</div>', unsafe_allow_html=True)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True
        )

        # Use the generator function with st.write_stream
        with st.container():
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(f"Error: {e}", icon="🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append({"role": "assistant", "content": combined_response})
