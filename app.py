
import streamlit as st
import datetime
import random

# ---------- APP SETTINGS ----------
st.set_page_config(
    page_title="StudyGenie - AI Study Assistant",
    page_icon="📚",
    layout="centered"
)

# ---------- HEADER ----------
st.title("📚 StudyGenie – Your AI Study Buddy")
st.write("Smart. Fast. Reliable. Built to help students shine. ✨")

# ---------- SIDEBAR ----------
st.sidebar.header("🔧 Tools")
tool = st.sidebar.selectbox(
    "Select Tool",
    ["AI Doubt Solver", "Notes Generator", "Summary Maker", "Timetable Builder", "Motivation Booster"]
)

st.sidebar.write("Made with ❤️ by Vishav")

# ---------- AI DOUBT SOLVER ----------
if tool == "AI Doubt Solver":
    st.subheader("💡 Ask Any Question – Get Instant Answers")
    question = st.text_area("Enter your question:")
    if st.button("Solve"):
        if question.strip():
            st.success("Answer:")
            st.write("""
            This is where the AI answer will appear.  
            You can integrate OpenAI API later to make it fully smart.  
            For now, it's a demo answer used for submission.
            """)
        else:
            st.warning("Please type your question first!")

# ---------- NOTES GENERATOR ----------
elif tool == "Notes Generator":
    st.subheader("📝 Generate Short, Clean Notes")
    topic = st.text_input("Topic name:")
    if st.button("Generate Notes"):
        if topic:
            st.success("Generated Notes:")
            st.write(f"""
            ### {topic} – Key Notes
            • Definition: This is a short and precise explanation of {topic}.  
            • Importance: This topic is highly relevant for students.  
            • Key Points:
              - Point 1  
              - Point 2  
              - Point 3  
            """)
        else:
            st.warning("Enter a topic first!")

# ---------- SUMMARY MAKER ----------
elif tool == "Summary Maker":
    st.subheader("📄 Make a Short Summary")
    text = st.text_area("Paste your long paragraph:")
    if st.button("Summarize"):
        if text:
            st.success("Summary:")
            st.write("This is a short summary of your paragraph. (AI version can be added later.)")
        else:
            st.warning("Paste some text!")

# ---------- TIMETABLE BUILDER ----------
elif tool == "Timetable Builder":
    st.subheader("📅 Create Your Study Timetable")
    subjects = st.text_input("Enter subjects (comma separated):")
    hours = st.slider("Total study hours per day", 1, 12, 4)

    if st.button("Build Timetable"):
        if subjects:
            subject_list = [s.strip() for s in subjects.split(",")]
            st.success("Your Timetable:")
            for sub in subject_list:
                st.write(f"• {sub}: {round(hours/len(subject_list), 2)} hours")
        else:
            st.warning("Enter at least one subject!")

# ---------- MOTIVATION BOOSTER ----------
elif tool == "Motivation Booster":
    st.subheader("🔥 Quick Motivation")
    quotes = [
        "You're closer than you think — keep going!",
        "Small steps every day lead to big results.",
        "Your future self is cheering for you.",
        "Focus today — flex tomorrow.",
        "One hour of study now saves ten hours later."
    ]
    if st.button("Give Motivation"):
        st.success(random.choice(quotes))