import streamlit as st
import requests
import json
import random
import time

# ---------------------------------------------------
# PAGE SETUP + LIGHT SOFT BACKGROUND + CUTE GEN Z FONT
# ---------------------------------------------------

st.set_page_config(page_title="StudyGenie Ultra", layout="wide")

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(170deg, #dff3ff, #f5dfff, #ffe6f2);
    background-size: cover !important;
    background-attachment: fixed !important;
    font-family: 'Poppins', sans-serif !important;
    color: #333;
}

.section {
    background: rgba(255, 255, 255, 0.45);
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.4);
    margin-top: 20px;
    backdrop-filter: blur(10px);
}

h1, h2, h3 {
    font-weight: 700;
    font-style: italic;
}

.genie-bubble {
    background: #ffffffa8;
    padding: 16px;
    margin: 12px 0;
    border-radius: 14px;
    border-left: 4px solid #a88bff;
    animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.98); }
    to { opacity: 1; transform: scale(1); }
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown(
    "<h1 style='text-align:center;color:#4a3b8f;'>✨ StudyGenie AI – Your Personal AI Study Bestie 💕</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:#5f569b;font-size:18px;'>Always here for your doubts, your dreams, and your glow-up ✨</p>",
    unsafe_allow_html=True
)

# ---------------------------------------------------
# AI CALL (GPT-5-mini)
# ---------------------------------------------------

def ask_ai(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
    }

    payload = {
        "model": "gpt-4.1-mini",  # safest + closest to GPT-5-mini tier
        "messages": [{
            "role": "user",
            "content": (
                "Your personality: warm, personal, encouraging, Gen-Z soft tone.\n"
                "Always reply short, crisp, helpful.\n\n" + prompt
            )
        }],
        "max_tokens": 1500,
        "temperature": 0.65
    }

    try:
        req = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=25
        )
        result = req.json()

        if "choices" not in result:
            return "⚠️ Bestie the AI got confused for a sec—try again."

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return "❌ Error: " + str(e)


# ---------------------------------------------------
# SIDEBAR — ALL ADVANCED FEATURES
# ---------------------------------------------------

tool = st.sidebar.radio(
    "✨ Choose your tool",
    [
        "AI Doubt Solver",
        "Notes Generator",
        "Summary Maker",
        "Timetable Builder",
        "Motivation Booster",
        "Flashcards",
        "Brain-Dump Cleaner",
        "Answer Checker",
        "AI Planner",
        "Mindset Reset",
        "Study Routine Designer",
        "Exam Strategy Maker",
        "Personal Study Coach"
    ]
)

# ---------------------------------------------------
# FEATURE: AI DOUBT SOLVER
# ---------------------------------------------------

if tool == "AI Doubt Solver":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("💡 Ask your doubt")

    q = st.text_area("Your question bestie:")

    if st.button("Solve it 💜"):
        if q.strip():
            with st.spinner("Thinking like a genius bestie..."):
                ans = ask_ai(q)
            st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
        else:
            st.warning("Write your doubt babe 💕")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# NOTES GENERATOR
# ---------------------------------------------------

elif tool == "Notes Generator":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("📘 Aesthetic Notes")

    topic = st.text_input("Topic:")
    if st.button("Generate Notes ✨"):
        if topic.strip():
            ans = ask_ai(f"Make crisp cute notes on: {topic}")
            st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# SUMMARY MAKER
# ---------------------------------------------------

elif tool == "Summary Maker":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🧾 Ultra Summary")

    txt = st.text_area("Paste something to summarize:")

    if st.button("Summarize ✨"):
        if txt.strip():
            ans = ask_ai("Summarize this clearly, short, crisp:\n" + txt)
            st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# TIMETABLE BUILDER
# ---------------------------------------------------

elif tool == "Timetable Builder":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("📅 Cute Study Timetable")

    subjects = st.text_input("Subjects separated with commas:")
    hrs = st.slider("Hours per day:", 1, 12, 5)

    if st.button("Create ✨"):
        if subjects.strip():
            subs = [s.strip() for s in subjects.split(",")]
            each = round(hrs / len(subs), 2)

            output = "✨ **Your Aesthetic Timetable**\n"
            for s in subs:
                output += f"📘 {s}: **{each} hours**\n"

            st.markdown(f"<div class='genie-bubble'>{output}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# MOTIVATION BOOSTER
# ---------------------------------------------------

elif tool == "Motivation Booster":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🔥 Motivation ")

    quotes = [
        "Your efforts today shape the life you will enjoy tomorrow.",
        "You deserve peace, progress, and pride in your work.",
        "Every step forward—no matter how small—counts.",
        "The future you imagine can become real with consistent effort.",
        "Your hard work will become your comfort one day.",
        "Strength grows every time you choose discipline.",
        "The version of you that you are building is outstanding.",
        "You do not need perfection, you only need consistency.",
        "Your dreams are possible because you are capable.",
        "Your dedication will lead to extraordinary results."
    ]

    if st.button("Boost Me ✨"):
        st.markdown(
            f"<div class='genie-bubble'>{random.choice(quotes)}</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# MORE FEATURES BELOW (FULLY WORKING)
# ---------------------------------------------------

elif tool == "Flashcards":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🃏 Flashcards")

    topic = st.text_input("Topic:")

    if st.button("Generate Flashcards ✨"):
        if topic.strip():
            ans = ask_ai(f"Make 6 simple flashcards for: {topic}")
            st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif tool == "Brain-Dump Cleaner":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🧠 Clean up your thoughts")

    dump = st.text_area("What is messy inside your brain:")

    if st.button("Organize It ✨"):
        if dump.strip():
            ans = ask_ai("Organize this neatly:\n" + dump)
            st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif tool == "Answer Checker":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("✔️ Check Your Answer")

    your = st.text_area("Your Answer:")
    corr = st.text_area("Correct Answer:")

    if st.button("Check ✨"):
        if your.strip() and corr.strip():
            ans = ask_ai(f"Compare student's answer to correct answer. Short, clear. Student: {your}. Correct: {corr}.")
            st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif tool == "AI Planner":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("📆 Daily Study Planner")

    goal = st.text_input("Your goal:")

    if st.button("Make Plan ✨"):
        if goal.strip():
            ans = ask_ai(f"Make a simple, clean daily plan for this goal: {goal}")
            st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# NEW: Mindset Reset
# ---------------------------------------------------

elif tool == "Mindset Reset":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🌸 Mindset Reset")

    if st.button("Reset My Mind ✨"):
        ans = ask_ai("Give a clean mindset reset, encouraging energy, long enough but not too long.")
        st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# NEW: Study Routine Designer
# ---------------------------------------------------

elif tool == "Study Routine Designer":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("📚 Study Routine Designer")

    hours = st.slider("How many hours you can study daily:", 1, 10, 4)

    if st.button("Design Routine ✨"):
        ans = ask_ai(f"Create a daily study routine for {hours} hours. Make it aesthetic, clean.")
        st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# NEW: Exam Strategy Maker
# ---------------------------------------------------

elif tool == "Exam Strategy Maker":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🎯 Exam Strategy")

    exam = st.text_input("Your exam:")

    if st.button("Build Strategy ✨"):
        ans = ask_ai(f"Make a high-impact exam strategy for: {exam}")
        st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# NEW: Personal Study Coach
# ---------------------------------------------------

elif tool == "Personal Study Coach":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("💞 StudyCoach – Personal Guidance")

    msg = st.text_area("Tell me what you’re struggling with:")

    if st.button("Coach Me ✨"):
        ans = ask_ai(f"You are their personal study coach. Respond to this with soft tone: {msg}")
        st.markdown(f"<div class='genie-bubble'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)