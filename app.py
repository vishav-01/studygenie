import streamlit as st
import requests
import json

# -------------------------
# 💗 UI DESIGN (Gen Z Gradient)
# -------------------------
st.set_page_config(page_title="StudyGenie AI", layout="centered")

st.markdown("""
<style>

body {
    background: linear-gradient(180deg, #3A0CA3, #7209B7, #F72585);
    font-family: 'Poppins', sans-serif;
}

.stTextInput > div > div > input {
    border-radius: 12px;
    border: 2px solid white;
}

.chat-bubble {
    padding: 16px;
    margin: 12px 0;
    border-radius: 18px;
    animation: pop 0.3s ease;
}

.user {
    background: rgba(255, 255, 255, 0.2);
    color: white;
}

.ai {
    background: rgba(0, 0, 0, 0.3);
    color: #ffe8fd;
}

@keyframes pop {
  0% {transform: scale(0.8);}
  100% {transform: scale(1);}
}

</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>✨ StudyGenie AI 2.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ffe6ff;'>Your smart bestie for solving every doubt 😭💗</p>", unsafe_allow_html=True)

# -------------------------
# 💗 CHAT MEMORY
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------
# 💗 DISPLAY CHAT HISTORY
# -------------------------
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "ai"
    st.markdown(f"<div class='chat-bubble {role}'>{msg['content']}</div>", unsafe_allow_html=True)

# -------------------------
# 💗 USER INPUT
# -------------------------
user_input = st.text_input("Ask anything bestie 💕:", "")

# -------------------------
# 💗 OPENAI REQUEST USING PURE REQUESTS (NO import openai)
# -------------------------
def call_openai_api(prompt):
    url = "https://api.openai.com/v1/chat/completions"   # gpt-4o-mini, gpt-5, etc.

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are StudyGenie, a friendly, smart doubt solver."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        return f"❌ Error: {response.text}"

    answer = response.json()["choices"][0]["message"]["content"]
    return answer

# -------------------------
# 💗 PROCESS USER MESSAGE
# -------------------------
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking for you bestie… 💕"):
        reply = call_openai_api(user_input)

    st.session_state.messages.append({"role": "ai", "content": reply})
    st.rerun()