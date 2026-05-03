import streamlit as st
import requests
import tempfile

#API_URL ="Your Ngrok URL"  # <-- change this

st.set_page_config(page_title="Therapist AI", layout="centered")
st.title("🧠 Therapist AI (API Mode)")

# -------------------------
# Session memory
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# -------------------------
# Display messages
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------
# TEXT INPUT
# -------------------------
user_text = st.chat_input("Type your message...")

if user_text:
    add_message("user", user_text)

    with st.chat_message("user"):
        st.write(user_text)

    # send to API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(
                    f"{API_URL}/chat",
                    json={"message": user_text},
                    timeout=120
                )
                response = res.json()["response"]
            except Exception as e:
                response = f"Error: {e}"

            st.write(response)

    add_message("assistant", response)

# -------------------------
# VOICE INPUT
# -------------------------
audio = st.audio_input("🎤 Speak")

if audio is not None:
    # Save audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio.read())
        audio_path = tmp.name

    # Add user message immediately
    add_message("user", audio_path)

    # Display user message
    with st.chat_message("user"):
        st.audio(audio_path)
        st.write("🎤 Voice message")

    # Send to backend
    with st.chat_message("assistant"):
        with st.spinner("Processing voice..."):
            try:
                with open(audio_path, "rb") as f:
                    res = requests.post(
                        f"{API_URL}/voice",
                        files={"file": ("audio.wav", f, "audio/wav")},
                        timeout=120
                    )

                try:
                    data = res.json()
                except Exception:
                    st.error("❌ Backend did not return JSON")
                    st.write("RAW:", res.text)
                    st.stop()

                transcription = data.get("transcription", "")
                response = data.get("response", "⚠️ No response")

            except Exception as e:
                transcription = ""
                response = f"Error: {e}"

            # Show transcription
            if transcription:
                st.write(f"🗣 {transcription}")

            # Show response
            st.write(response)

    # Save BOTH messages to history
    if transcription:
        add_message("user", f"🎤 {transcription}")
    else:
        add_message("user", audio_path)

    add_message("assistant", response)