import streamlit as st
import requests
import json
import random

# -------------------------------------
# PAGE + BACKGROUND
# -------------------------------------
st.set_page_config(page_title="StudyGenie AI", layout="centered")

bg_css = """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #3a0ca3, #7209b7, #f72585);
    background-size: cover !important;
    background-attachment: fixed !important;
    font-family: "Poppins", sans-serif;
}
.section-box {
    background: rgba(255, 255, 255, 0.15);
    padding: 20px;
    border-radius: 16px;
    backdrop-filter: blur(8px);
    color: white;
    margin-top: 20px;
}
</style>
"""
st.markdown(bg_css, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:white;'>✨ StudyGenie – Your AI Study Bestie 💕</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#ffe6ff;'>Ask, study, glow-up ✨</p>", unsafe_allow_html=True)

# -------------------------------------
# OPENAI FUNCTION
# -------------------------------------
def ask_openai(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=25
        )
        return res.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return "❌ Error contacting AI: " + str(e)

# -------------------------------------
# SIDEBAR TOOLS
# -------------------------------------
tool = st.sidebar.selectbox(
    "Choose a Feature",
    ["AI Doubt Solver", "Notes Generator", "Summary Maker",
     "Timetable Builder", "Motivation Booster"]
)

# =====================================
# AI DOUBT SOLVER
# =====================================
if tool == "AI Doubt Solver":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("💡 Ask any doubt bestie")

    q = st.text_area("Write your doubt:")
    if st.button("Solve Doubt"):
        if q.strip():
            with st.spinner("Thinking… 💞"):
                ans = ask_openai(q)
            st.success("✨ Your Answer:")
            st.write(ans)
        else:
            st.warning("Write something first bestie 😭")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================
# NOTES GENERATOR
# =====================================
elif tool == "Notes Generator":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📝 Generate Notes")

    topic = st.text_input("Topic Name:")
    if st.button("Generate Notes"):
        if topic.strip():
            prompt = f"Create simple, clean notes for the topic: {topic}."
            ans = ask_openai(prompt)
            st.success("📝 Notes:")
            st.write(ans)
        else:
            st.warning("Enter a topic first!")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================
# SUMMARY MAKER
# =====================================
elif tool == "Summary Maker":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("🧾 Make Summary")

    text = st.text_area("Paste text:")
    if st.button("Summarize"):
        if text.strip():
            ans = ask_openai(f"Summarize this: {text}")
            st.success("✨ Summary:")
            st.write(ans)
        else:
            st.warning("Paste something first!")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================
# TIMETABLE BUILDER
# =====================================
elif tool == "Timetable Builder":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📅 Study Timetable")

    subs = st.text_input("Subjects (comma separated):")
    hours = st.slider("Hours per day", 1, 12, 4)

    if st.button("Build Timetable"):
        if subs.strip():
            s_list = [s.strip() for s in subs.split(",")]
            time_each = round(hours / len(s_list), 2)

            st.success("✨ Your Timetable")
            for s in s_list:
                st.write(f"📘 {s}: **{time_each} hours**")

        else:
            st.warning("Add subjects first!")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================
# MOTIVATION BOOSTER
# =====================================
elif tool == "Motivation Booster":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("🔥 Boost Your Mood Bestie")

    quotes = [
        "Bestie you're literally ICONIC 😭🔥",
        "You will glow so hard people need sunglasses 😎💕",
        "Your future self is smiling rn 😭✨",
        "Trust me you’re built different.",
        "Focus now, flex forever 😤",
        "One study session today = massive win tomorrow 💗",
        "Babe you're not behind, you're loading 💞",
        "You’re smart AND hot, unbeatable combo 😭🔥",
        "Success is already flirting with you 😏💗",
        "Glow-up in progress… stay tuned ✨",
        "You’re doing so well even when you feel lost 💕",
        "Your dream uni is WAITING FOR YOU 😭🔥",
        "You're the main character today and everyday.",
        "You’ll look back and thank yourself for this.",
        "Study hard → K-drama life unlocked 💞",
        "You're energy is rare… protect it ✨",
        "Universe is literally rigged in your favour.",
        "You’re not tired, you're legendary.",
        "Future millionaire loading… 💸",
        "Trust the grind bestie, it loves you 😭",
        "Even your mistakes are cute 😭💕",
        "You’ve survived 100% of your bad days.",
        "You’re too powerful to quit now.",
        "Your potential is insane omg.",
        "Believe in yourself like I believe in you 💗",
        "Just one more chapter… future flex awaits 😎",
        "Studygenie loves you and hyping you ALWAYS ✨"
    ]

    if st.button("Boost Me ✨"):
        st.success(random.choice(quotes))

    st.markdown("</div>", unsafe_allow_html=True)