import streamlit as st
import random

st.set_page_config(
    page_title="StudyGenie - AI Study Buddy",
    page_icon="📚",
    layout="centered"
)

st.title("📚 StudyGenie – Your AI Study Bestie ✨")
st.write("Ask questions, make notes, summaries, timetables and get motivation!")

# --- SIDEBAR ---
st.sidebar.header("Tools")
tool = st.sidebar.selectbox(
    "Choose a feature",
    ["AI Doubt Solver", "Notes Generator", "Summary Maker", "Timetable Builder", "Motivation Booster"]
)

# =======================
# DOUBT SOLVER
# =======================
if tool == "AI Doubt Solver":
    st.subheader("💡 Ask any academic doubt")
    question = st.text_area("Type your question here:")

    if st.button("Solve"):
        if question.strip():
            st.success("This is where the AI answer will appear. (Add API key later)")
        else:
            st.warning("Please type a question first!")

# =======================
# NOTES GENERATOR
# =======================
elif tool == "Notes Generator":
    st.subheader("📝 Generate notes for any topic")
    topic = st.text_input("Enter topic name:")

    if st.button("Generate Notes"):
        if topic.strip():
            st.success("Generated Notes:")
            st.write(f"""
### {topic}
• Key point 1  
• Key point 2  
• Key point 3  
            """)
        else:
            st.warning("Enter a topic first!")

# =======================
# SUMMARY MAKER
# =======================
elif tool == "Summary Maker":
    st.subheader("📄 Make short summary")
    text = st.text_area("Paste paragraph:")

    if st.button("Summarize"):
        if text.strip():
            st.success("Summary:")
            st.write("Short summary appears here. (AI needed)")
        else:
            st.warning("Paste something first!")

# =======================
# TIMETABLE BUILDER
# =======================
elif tool == "Timetable Builder":
    st.subheader("📅 Build timetable")
    subjects = st.text_input("Enter subjects (comma separated):")
    hours = st.slider("Study hours per day", 1, 12, 4)

    if st.button("Create Timetable"):
        if subjects.strip():
            names = [s.strip() for s in subjects.split(",")]
            time = round(hours / len(names), 2)

            st.success("Your Timetable")
            for s in names:
                st.write(f"• {s}: {time} hrs")
        else:
            st.warning("Enter at least one subject!")

# =======================
# MOTIVATION BOOSTER
# =======================
elif tool == "Motivation Booster":
    st.subheader("🔥 Motivation Booster")
    quotes = [
        "Bestie you got this 😭🔥",
        "One step today = massive glow tomorrow ✨",
        "Your future self is cheering for you 💗",
        "Focus now, flex forever 😤",
        "You’re literally unstoppable, babe."
    ]

    if st.button("Boost Me"):
        st.success(random.choice(quotes))