import secrets
import time
import streamlit as st
from api_client import ApiError, ask
from settings import UI_PASSWORD

COOLDOWN_SECONDS = 60
st.set_page_config(page_title="Agentic RAG Demo", page_icon="🤖")
st.title("Agentic RAG Demo")


def check_password() -> None:
    if not UI_PASSWORD or st.session_state.get("authenticated"):
        return

    password = st.text_input("Demo password", type="password")
    if password:
        if secrets.compare_digest(password.encode(), UI_PASSWORD.encode()):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password.")
    st.stop()


def show_details(result: dict) -> None:
    if result["sources"]:
        st.caption("Sources: " + ", ".join(result["sources"]))
    with st.expander("How the agent decided"):
        st.write(f"Route: **{result['route']}**")
        st.write(f"Rewrites: **{result['rewrites']}**")
        if result["critic_reason"]:
            st.write(f"Critic: {result['critic_reason']}")


check_password()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.sidebar.header("Your OpenAI API key")
openai_key = st.sidebar.text_input(
    "OpenAI API key", type="password", placeholder="sk-..."
).strip()
st.sidebar.caption(
    "Your key is used only to answer your questions. It is sent to this demo's "
    "API over HTTPS with each request and is not stored or logged. "
    "Use a key with a small spending limit and delete it after testing."
)
if st.sidebar.button("Clear chat"):
    st.session_state.messages = []
    st.rerun()

if not openai_key:
    st.info("Enter your OpenAI API key in the sidebar to start chatting.")
    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("details"):
            show_details(message["details"])

remaining = int(st.session_state.get("cooldown_until", 0) - time.time())
in_cooldown = remaining > 0

question = st.chat_input(
    "Ask about refunds, shipping or account security...",
    max_chars=500,
    disabled=in_cooldown,
)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                result = ask(question, openai_key)
        except ApiError as exc:
            if exc.status_code == 429 and "too many requests" in str(exc).lower():
                st.session_state.cooldown_until = time.time() + COOLDOWN_SECONDS
                st.rerun()
            st.error(str(exc))
        else:
            st.markdown(result["answer"])
            show_details(result)
            st.session_state.messages.append(
                {"role": "assistant", "content": result["answer"], "details": result}
            )

if in_cooldown:
    st.warning(f"Too many requests. You can send your next message in {remaining} seconds.")
    time.sleep(1)
    st.rerun()