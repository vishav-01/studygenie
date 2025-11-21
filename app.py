import streamlit as st
import random
import time
import requests

def google_brain(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
    data = requests.get(url).json()
    return data.get("Abstract", "No direct answer found.")


st.set_page_config(
    page_title="StudyGenie – Offline Mode",
    page_icon="✨",
    layout="centered"
)

# ---------------- CUSTOM UI STYLE ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
    font-family: 'Poppins', sans-serif;
}
.block-container {
    background: rgba(255,255,255,0.22);
    padding: 2rem;
    border-radius: 20px;
    backdrop-filter: blur(20px);
}
</style>
""", unsafe_allow_html=True)

# ---------------- MAIN TITLE ----------------
st.title("✨ StudyGenie –  Smart Study bestie 💗")
st.write("⚡")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Tools")
tool = st.sidebar.selectbox(
    "Choose a feature",
    ["AI Doubt Solver (Offline)", "Notes Generator", "Summary Maker", "Timetable Builder", "Motivation Booster"]
)

# ===========================
# 1. OFFLINE DOUBT SOLVER
# ===========================
if tool == "AI Doubt Solver (Offline)":
    st.subheader("💡 Ask your doubt (offline version)")

    question = st.text_area("Your question:")

    if st.button("Solve"):
        if question.strip():

            st.info("Thinking… (offline logic) ✨")
            time.sleep(1.2)

            # Offline rule-based responses
            if "what is" in question.lower():
                st.success("This looks like a definition question. Explain it like this:")
                st.write("👉 A simple definition:\n\n• Start with meaning\n• Add example\n• End with importance")

            elif "why" in question.lower():
                st.success("Here's how to answer WHY questions:")
                st.write("👉 Explain the cause, effect, and real-life relevance.")

            elif "how" in question.lower():
                st.success("Here's how to answer HOW questions:")
                st.write("👉 Explain steps, process, and result.")

            else:
                st.success("General Answer Format:")
                st.write("👉 Intro → Explanation → Example → Conclusion")

        else:
            st.warning("Ask something first!")

# ===========================
# 2. NOTES GENERATOR (OFFLINE)
# ===========================
elif tool == "Notes Generator":
    st.subheader("📝 Generate notes (offline version)")
    topic = st.text_input("Topic name:")

    if st.button("Generate Notes"):
        if topic.strip():

            st.success("✨ Your Notes:")
            st.write(f"""
### {topic.title()}
• Meaning  
• Key features  
• Examples  
• Importance  
• Real-world application  
""")

        else:
            st.warning("Enter a topic first!")

# ===========================
# 3. SUMMARY MAKER (OFFLINE)
# ===========================
elif tool == "Summary Maker":
    st.subheader("📄 Offline Summary Maker")
    text = st.text_area("Paste paragraph:")

    if st.button("Summarize"):
        if text.strip():

            st.success("✨ Summary:")
            st.write("• Main idea\n• 2–3 key points\n• Final conclusion")

        else:
            st.warning("Paste something first!")

# ===========================
# 4. TIMETABLE BUILDER
# ===========================
elif tool == "Timetable Builder":
    st.subheader("📅 Build your timetable")
    subjects = st.text_input("Subjects (comma separated):")
    hours = st.slider("Daily Study Hours", 1, 12, 4)

    if st.button("Create Timetable"):
        if subjects.strip():
            subs = [s.strip() for s in subjects.split(",")]
            per = round(hours / len(subs), 2)

            st.success("✨ Your Timetable")
            for s in subs:
                st.write(f"• {s}: {per} hrs")

        else:
            st.warning("Enter subjects first!")

# ===========================
# 5. MOTIVATION BOOSTER (BIG LIST)
# ===========================
elif tool == "Motivation Booster":
    st.subheader("🔥 Motivation Booster")

    quotes = [
        "You’re literally unstoppable bestie 🔥",
        "Your glow-up is coming. Don’t stop now ✨",
        "Study now, flex in Korea later 😭🔥",
        "Your future self is proud of you 💞",
        "Every day you’re getting stronger 🌟",
        "You have no idea how powerful you are 😤",
        "Discipline > Motivation. Stay locked in 🔥",
        "Your dreams are valid. Keep going 💗",
        "Small progress is still progress 🌸",
        "Your success arc is loading… 99% ✨",
        "Bestie your potential scares people 😭🔥",
        "Imagine quitting now? No way 🤨🔥",
        "You're building a future people dream of 💫",
        "Your goals aren’t random — they're your calling 💙",
        "You’re one chapter away from your breakthrough 📘",
        "Slowly, quietly… you’re becoming the person you wanted 💗",
        "The universe is aligning for you ✨",
        "The effort you put today will save your future self 😭🔥",
        "You’re not behind. You’re preparing 💞",
        "Bestie… you’re destined for greatness 🌟",
        "Don’t underestimate your own power 🔥",
        "Your discipline is your superpower 💙",
        "Level up quietly, glow loudly ✨",
        "Winning is on your destiny babe 💗",
        "Korea is waiting for your arrival 😤🔥",
    ]

    if st.button("Boost Me"):
        st.success(random.choice(quotes))