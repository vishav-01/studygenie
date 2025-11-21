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
    background: linear-gradient(180deg, #c6e6ff, #e7c6ff, #ffd6e7);
    background-size: cover !important;
    background-attachment: fixed !important;
    font-family: 'Poppins', sans-serif;
}

.section-box {
    background: rgba(255, 255, 255, 0.45);
    padding: 22px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    color: #333;
    margin-top: 18px;
    border: 1px solid rgba(255, 255, 255, 0.4);
}

h1, h2, h3, h4 {
    font-weight: 700;
    font-style: italic;
}
</style>
"""
st.markdown(bg_css, unsafe_allow_html=True)

st.markdown(
    "<h1 style='text-align:center;color:#4a4a4a;'>✨ StudyGenie – Your AI Study Bestie 💕</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center;color:#5f4b8b;'>Ask, learn, glow, repeat ✨</p>",
    unsafe_allow_html=True,
)

# -------------------------------------
# AI FUNCTION (GPT-4.5 / 5-mini)
# -------------------------------------

def ask_ai(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
    }

    data = {
        "model": "gpt-4.1-mini",   # safest + stable model
        "messages": [{
            "role": "user",
            "content": "Give short, crisp, Gen-Z friendly study answers.\n\n" + prompt
        }],
        "max_tokens": 350,
        "temperature": 0.6
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=25
        )
        data = response.json()

        # PROPER ERROR FIX
        if "choices" not in data:
            return "⚠️ AI response invalid. Try again in a moment."

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return "❌ AI error: " + str(e)


# -------------------------------------
# SIDEBAR TOOLS
# -------------------------------------
tool = st.sidebar.selectbox(
    "Choose a Feature",
    [
        "AI Doubt Solver", "Notes Generator", "Summary Maker",
        "Timetable Builder", "Motivation Booster",
        "Flashcards", "Brain-Dump Cleaner", "Answer Checker",
        "AI Planner"
    ]
)


# -------------------------------------
# FEATURES
# -------------------------------------

# AI DOUBT SOLVER
if tool == "AI Doubt Solver":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("💡 Ask any doubt")

    q = st.text_area("Type your doubt")
    if st.button("Solve"):
        if q.strip():
            ans = ask_ai(q)
            st.success("✨ Answer:")
            st.write(ans)
        else:
            st.warning("Write something first bestie 💗")
    st.markdown("</div>", unsafe_allow_html=True)


# NOTES GENERATOR
elif tool == "Notes Generator":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📝 Notes Generator")

    t = st.text_input("Topic:")
    if st.button("Generate Notes"):
        if t.strip():
            ans = ask_ai(f"Make short crisp notes for: {t}")
            st.success("📘 Notes:")
            st.write(ans)
        else:
            st.warning("Enter a topic!")
    st.markdown("</div>", unsafe_allow_html=True)


# SUMMARY MAKER
elif tool == "Summary Maker":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("🧾 Summary")

    text = st.text_area("Paste text")
    if st.button("Summarize"):
        if text.strip():
            ans = ask_ai("Summarize this in short points: " + text)
            st.success("✨ Summary:")
            st.write(ans)
        else:
            st.warning("Paste something!")
    st.markdown("</div>", unsafe_allow_html=True)


# TIMETABLE BUILDER
elif tool == "Timetable Builder":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📅 Study Timetable")

    subs = st.text_input("Subjects (comma separated)")
    hrs = st.slider("Hours per day", 1, 12, 4)

    if st.button("Create"):
        if subs.strip():
            s_list = [s.strip() for s in subs.split(",")]
            each = round(hrs / len(s_list), 2)

            st.success("✨ Your Timetable:")
            for s in s_list:
                st.write(f"📘 {s}: **{each} hours**")
        else:
            st.warning("Add at least one subject!")
    st.markdown("</div>", unsafe_allow_html=True)


# MOTIVATION BOOSTER
elif tool == "Motivation Booster":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("🔥 Motivation")

    quotes = [
        "You are going to be a legendary version of yourself.",
        "Your future self is going to be proud.",
        "Every chapter you finish rewrites your destiny.",
        "Discipline is the bridge between you and your dream life.",
        "Your glow-up era is arriving quietly.",
        "Small progress today becomes big progress later.",
        "You deserve the life you imagine.",
        "Your effort today becomes your comfort tomorrow.",
        "Strength grows in silence, keep going.",
        "Your potential is louder than your doubts."
    ]

    if st.button("Boost Me"):
        st.success(random.choice(quotes))
    st.markdown("</div>", unsafe_allow_html=True)


# FLASHCARDS
elif tool == "Flashcards":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("🃏 Flashcards")

    topic = st.text_input("Topic:")
    if st.button("Generate Flashcards"):
        if topic.strip():
            ans = ask_ai(f"Make 5 simple flashcards for: {topic}")
            st.success("Flashcards:")
            st.write(ans)
        else:
            st.warning("Enter a topic!")
    st.markdown("</div>", unsafe_allow_html=True)


# BRAIN-DUMP CLEANER
elif tool == "Brain-Dump Cleaner":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("🧠 Brain Dump Cleanup")

    dump = st.text_area("Write your messy thoughts")
    if st.button("Clean it"):
        if dump.strip():
            ans = ask_ai(f"Organize this into clean points: {dump}")
            st.success("Processed:")
            st.write(ans)
        else:
            st.warning("Write something!")
    st.markdown("</div>", unsafe_allow_html=True)


# ANSWER CHECKER
elif tool == "Answer Checker":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("✔️ Answer Checker")

    q = st.text_area("Your Answer:")
    corr = st.text_area("Correct Answer:")
    if st.button("Check"):
        if q.strip() and corr.strip():
            ans = ask_ai(f"Compare student's answer with correct answer. Be short. Student: {q}. Correct: {corr}.")
            st.success("Result:")
            st.write(ans)
        else:
            st.warning("Fill both boxes!")
    st.markdown("</div>", unsafe_allow_html=True)


# AI PLANNER
elif tool == "AI Planner":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📆 AI Study Planner")

    goal = st.text_input("Your goal:")
    if st.button("Plan"):
        if goal.strip():
            ans = ask_ai(f"Make a simple daily plan to achieve: {goal}")
            st.success("Plan:")
            st.write(ans)
        else:
            st.warning("Enter a goal!")
    st.markdown("</div>", unsafe_allow_html=True)