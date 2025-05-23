import streamlit as st
import google.generativeai as genai

st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="centered",
)

# 🔑 Gemini credentials
API_KEY = st.secrets["gemini"]["api_key"]
MODEL_NAME = "models/gemini-1.5-flash"
TEMPERATURE = 0.7

genai.configure(api_key=API_KEY)

# 🗂 Session state init
if "chat" not in st.session_state:
    st.session_state.chat = genai.GenerativeModel(MODEL_NAME).start_chat()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions" not in st.session_state:
    st.session_state.sessions = []
if "current_saved" not in st.session_state:
    st.session_state.current_saved = False  # track if this chat is already saved


# ✅ Save current chat only once
def save_current_chat_once():
    if not st.session_state.current_saved and st.session_state.messages:
        first_user_msg = next(
            (m["content"] for m in st.session_state.messages if m["role"] == "user"), "Chat"
        )
        title = first_user_msg[:40] + ("…" if len(first_user_msg) > 40 else "")
        st.session_state.sessions.append({
            "title": title,
            "messages": st.session_state.messages.copy()
        })
        st.session_state.current_saved = True


# ===============================
# 📌 SIDEBAR – New Chat & History
# ===============================
with st.sidebar:
    if st.button("🆕 New Chat", use_container_width=True):
        save_current_chat_once()
        st.session_state.chat = genai.GenerativeModel(MODEL_NAME).start_chat()
        st.session_state.messages = []
        st.session_state.current_saved = False
        st.rerun()

    st.markdown("### 📜 Chat History")
    save_current_chat_once()  # auto-save first time message starts the session
    if st.session_state.sessions:
        for idx, sess in enumerate(reversed(st.session_state.sessions)):
            if st.button(sess["title"], key=f"hist_{idx}", use_container_width=True):
                st.session_state.messages = sess["messages"].copy()
                st.session_state.chat = genai.GenerativeModel(MODEL_NAME).start_chat()
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        st.session_state.chat.send_message(msg["content"])
                st.session_state.current_saved = True
                st.rerun()
    else:
        st.caption("No saved chats yet.")

    st.markdown("---")


# =====================
# 💬 MAIN CHAT WINDOW
# =====================
st.title("🤖 Gemini Chatbot")

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])

# Input & Response
user_input = st.chat_input("Ask me anything…")
if user_input:
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Gemini is thinking…"):
            try:
                response = st.session_state.chat.send_message(
                    user_input,
                    generation_config={"temperature": TEMPERATURE}
                )
                reply_text = response.text.strip()
            except Exception as e:
                reply_text = f"❌ Error: {e}"
        st.markdown(reply_text)
    st.session_state.messages.append({"role": "assistant", "content": reply_text})

    save_current_chat_once()  # Save to history if it's the first user message

# 🌈 CSS
st.markdown("""
<style>
section.main > div { padding-top: 1.3rem; }
.stChatMessage.content { width: 100%; }
</style>
""", unsafe_allow_html=True)
