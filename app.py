# -----------------------------------------------------
# STUDYGENIE — Aesthetic AI Study Buddy (Working Model)
# -----------------------------------------------------

import streamlit as st
import requests
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="StudyGenie – AI Bestie",
    page_icon="✨",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    * {
        font-family: 'Poppins', sans-serif !important;
    }

    body {
        background: linear-gradient(135deg, #7F7BFF, #B06BFF, #FF71C0);
        animation: gradientMove 8s infinite alternate ease-in-out;
        background-size: 400% 400%;
    }

    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }

    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: white;
        text-shadow: 0px 4px 18px rgba(0,0,0,0.4);
        animation: zoomIn 0.8s ease;
    }

    @keyframes zoomIn {
        0% { transform: scale(0.7); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    .box {
        background: rgba(255,255,255,0.13);
        padding: 25px;
        border-radius: 20px;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.3);
        animation: fadeIn 1s ease;
        color: white;
    }

    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    </style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<div class='main-title'>📚 StudyGenie – Your AI Bestie 💜✨</div>", unsafe_allow_html=True)
st.write("Ask doubts, make notes, summaries, timetables, and glow up academically babe 😭💗")

# ---------------- SIDEBAR ----------------
st.sidebar.header("✨ Tools")
tool = st.sidebar.selectbox(
    "Choose a feature",
    ["AI Doubt Solver", "Notes Generator", "Summary Maker", "Timetable Builder", "Motivation Booster"]
)

# ----------- AI ANSWER FUNCTION (Gemini / OpenAI) ------------
def ask_ai(question, model="gemini"):
    try:
        if model == "gemini":
            API_KEY = "YOUR_GEMINI_API_KEY"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

            data = { "contents": [ { "parts": [ { "text": question } ] } ] }
            res = requests.post(url, json=data).json()
            return res["candidates"][0]["content"]["parts"][0]["text"]

        else:
            from openai import OpenAI
            client = OpenAI(api_key="YOUR_OPENAI_KEY")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": question}]
            )
            return response.choices[0].message.content

    except:
        return "Something went wrong 😭💔. Check your API key bestie."

# ------------------ FEATURES ------------------

# AI DOUBT SOLVER
if tool == "AI Doubt Solver":
    st.markdown("<div class='box'>💡 Ask any academic doubt</div>", unsafe_allow_html=True)
    question = st.text_area("Type your question:")

    if st.button("Solve ✨"):
        if question.strip():
            with st.spinner("Your AI bestie is thinking... 😭✨"):
                answer = ask_ai(question)
                st.success("✨ Answer:")
                st.write(answer)
        else:
            st.warning("Write something bestie 😭💗")


# NOTES GENERATOR
elif tool == "Notes Generator":
    st.markdown("<div class='box'>📝 Generate Notes</div>", unsafe_allow_html=True)
    topic = st.text_input("Topic name:")

    if st.button("Generate Notes 📄"):
        if topic.strip():
            text = ask_ai(f"Make clean student notes on: {topic}")
            st.success("Notes:")
            st.write(text)
        else:
            st.warning("Enter a topic bestie!")


# SUMMARY MAKER
elif tool == "Summary Maker":
    st.markdown("<div class='box'>📄 Summary Maker</div>", unsafe_allow_html=True)
    text = st.text_area("Paste paragraph:")

    if st.button("Summarize ✂️"):
        if text.strip():
            summary = ask_ai(f"Summarize this in simple words:\n{text}")
            st.success("Summary:")
            st.write(summary)
        else:
            st.warning("Paste something babe 😭")


# TIMETABLE BUILDER
elif tool == "Timetable Builder":
    st.markdown("<div class='box'>📅 Timetable Builder</div>", unsafe_allow_html=True)
    subjects = st.text_input("Subjects (comma separated):")
    hours = st.slider("Study hours/day", 1, 12, 4)

    if st.button("Create 🕒"):
        if subjects.strip():
            names = [s.strip() for s in subjects.split(",")]
            time = round(hours / len(names), 2)
            st.success("Your Study Plan ✨")
            for s in names:
                st.write(f"• **{s}** — {time} hrs")
        else:
            st.warning("Enter subjects!")


# MOTIVATION BOOSTER
elif tool == "Motivation Booster":
    st.markdown("<div class='box'>🔥 Motivation Booster</div>", unsafe_allow_html=True)

    quotes = [
        "Bestie you’re literally built for greatness 😭🔥",
        "One focused year = dream life unlocked ✨",
        "Your future self is flexing because of you 💗",
        "Work now, glow forever 😤💜",
        "You’re not behind. You’re loading 💫",
        "The world isn’t ready for your success arc 😭",
        "Silent grind, loud results ✨",
        "You’re the main character babe 💗",
        "Mindset > Everything 💜",
        "Do it for your future aesthetic self 🔥",
        "You’re powerful even on your bad days.",
        "Trust the process — magic is brewing ✨",
        "Don't stop. Your blessings are walking toward you 💗",
        "Stay consistent — the universe is watching 👀",
        "Every day you’re evolving into your best version 😭",
        "Prove your old self right 🔥",
        "Study like your soulmate is Korean 😭🔥",
        "Glow up mentally, physically, academically 💜",
        "Your haters are checking your story rn 😭💀",
        "Next 6 months = new you.",
        "Smart, cute, disciplined = unbeatable combo 💗",
        "Dreams don’t work unless you do ✨",
        "Your success era is officially loading… ⚡",
        "You’re rare. Act like it 💜",
        "If you don’t give up, you win 🔥"
    ]

    if st.button("Boost Me ✨"):
        st.success(random.choice(quotes))