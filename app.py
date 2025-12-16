import streamlit as st
import requests
import json

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="StudyGenie — AI Bestie", layout="wide")

# =====================================================
# SIDEBAR — THEME + TOOLS (LIKE IMAGE)
# =====================================================
with st.sidebar:
    st.markdown("### 🎨 Choose Theme")
    theme = st.selectbox(
        "",
        ["Doraemon Blue", "Sky Blue", "Soft Pink", "Lavender"]
    )

    st.markdown("---")
    st.markdown("### 😘 StudyGenie — Your AI Bestie 💖")

    tool = st.radio(
        "Choose a Tool ✨",
        [
            "AI Planner",
            "Mindset Reset",
            "Study Routine Designer",
            "Exam Strategy Maker",
            "Personal Study Coach"
        ]
    )

# =====================================================
# THEME COLORS (FLAT, NO GRADIENT)
# =====================================================
theme_colors = {
    "Doraemon Blue": "#2ea3f2",
    "Sky Blue": "#6ecbff",
    "Soft Pink": "#ff9fcf",
    "Lavender": "#bfa8ff"
}

bg_color = theme_colors[theme]

# =====================================================
# APPLY UI STYLE (MATCH IMAGE)
# =====================================================
st.markdown(f"""
<style>
html, body, [data-testid="stAppViewContainer"] {{
    background-color: {bg_color};
    color: white;
    font-family: 'Poppins', sans-serif;
}}

section[data-testid="stSidebar"] {{
    background-color: #8fd0ff;
}}

h1 {{
    font-size: 34px;
    margin-bottom: 10px;
}}

textarea {{
    border-radius: 10px !important;
}}

.response {{
    margin-top: 15px;
    padding: 15px;
    background: rgba(255,255,255,0.2);
    border-radius: 10px;
}}
</style>
""", unsafe_allow_html=True)

# =====================================================
# AI CALL (SAFE + WORKING)
# =====================================================
def ask_ai(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
    }

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": 0.6
    }

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=20
        )
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "⚠️ AI error — check API key."

# =====================================================
# MAIN CONTENT AREA (LIKE IMAGE)
# =====================================================
st.markdown(f"## ✨ {tool} ✨")

user_input = st.text_area("Type your message 💬")

col1, col2 = st.columns([1, 2])

with col1:
    send = st.button("Send")

with col2:
    clear = st.button("Clear")

if clear:
    st.rerun()

if send and user_input.strip():
    prompt_map = {
        "AI Planner": f"Create a simple daily plan for: {user_input}",
        "Mindset Reset": "Give a calm, motivating mindset reset.",
        "Study Routine Designer": f"Create a study routine for {user_input} hours.",
        "Exam Strategy Maker": f"Create an exam strategy for {user_input}.",
        "Personal Study Coach": f"You are a kind study coach. Help with: {user_input}"
    }

    reply = ask_ai(prompt_map[tool])
    st.markdown(f"<div class='response'>{reply}</div>", unsafe_allow_html=True)