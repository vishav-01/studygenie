import streamlit as st
import random
import openai
# Page setup
st.set_page_config(
    page_title="StudyGenie - AI Study Bestie",
    page_icon="📚",
    layout="centered"
)

st.title("📚 StudyGenie — Your AI Study Bestie 💞✨")
st.write("Ask doubts, generate notes, make summaries, build timetables, and get motivation — all in bestie mode 😤💗")

# Load API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# AI function
def get_ai_answer(question):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are StudyGenie — a cute, playful, Gen-Z AI bestie "
                    "who explains concepts clearly, motivates the user, and talks in a loving, energetic tone."
                )
            },
            {"role": "user", "content": question}
        ]
    )
    return response["choices"][0]["message"]["content"]


# Sidebar tools
st.sidebar.header("Tools")
tool = st.sidebar.selectbox(
    "Choose a feature",
    [
        "AI Doubt Solver",
        "Notes Generator",
        "Summary Maker",
        "Timetable Builder",
        "Motivation Booster"
    ]
)


# =========================================
# DOUBT SOLVER
# =========================================
if tool == "AI Doubt Solver":
    st.subheader("💡 Ask any doubt — bestie solves it 💞")
    q = st.text_area("Type your question:")

    if st.button("Solve My Doubt"):
        if q.strip():
            with st.spinner("Bestie wait, I’m cooking your answer 😤💗"):
                answer = get_ai_answer(q)
                st.success(answer)
        else:
            st.warning("Type something bestie 😭")


# =========================================
# NOTES GENERATOR
# =========================================
elif tool == "Notes Generator":
    st.subheader("📝 Generate clean notes on any topic")
    topic = st.text_input("Enter topic:")

    if st.button("Generate Notes"):
        if topic.strip():
            with st.spinner("Making notes for you babe… 💞✨"):
                answer = get_ai_answer(f"Make short notes on: {topic}")
                st.success(answer)
        else:
            st.warning("Enter a topic first 😩")


# =========================================
# SUMMARY MAKER
# =========================================
elif tool == "Summary Maker":
    st.subheader("📄 Summarize long paragraphs")
    text = st.text_area("Paste paragraph:")

    if st.button("Summarize"):
        if text.strip():
            with st.spinner("Summarizing with love 💗"):
                answer = get_ai_answer(f"Summarize this in simple words: {text}")
                st.success(answer)
        else:
            st.warning("Paste something babe 😭")


# =========================================
# TIMETABLE BUILDER
# =========================================
elif tool == "Timetable Builder":
    st.subheader("📅 Auto-build study timetable")
    subjects = st.text_input("Subjects (comma separated):")
    hours = st.slider("Study hours per day:", 1, 12, 4)

    if st.button("Create Timetable"):
        if subjects.strip():
            subs = [s.strip() for s in subjects.split(",")]
            per = round(hours / len(subs), 2)

            st.success("Your Study Timetable 💞✨")
            for s in subs:
                st.write(f"• **{s}** → {per} hours")
        else:
            st.warning("Enter subjects babe 😭")


# =========================================
# MOTIVATION BOOSTER
# =========================================
elif tool == "Motivation Booster":
    st.subheader("🔥 Let bestie hype you up")
    quotes = [
        "Bestie you're literally unstoppable 😭🔥",
        "Future you is clapping for you rn 💗",
        "Study now, glow later 😩✨",
        "Focus mode ON, distractions OUT 😤",
        "I believe in you more than anyone 😭💞"
    ]

    if st.button("Boost Me"):
        st.success(random.choice(quotes))