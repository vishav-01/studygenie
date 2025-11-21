import streamlit as st
import random
import OpenAI

st.set_page_config(
    page_title="StudyGenie – Your AI Bestie",
    page_icon="✨",
    layout="centered"
)

# -------------------------------
# CUSTOM CSS FOR AESTHETIC VIBE
# -------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #8ec5fc 0%, #e0c3fc 100%);
    font-family: 'Poppins', sans-serif;
}
h1, h2, h3, h4 {
    color: white;
    text-shadow: 0px 0px 10px rgba(255,255,255,0.7);
}
.block-container {
    background: rgba(255,255,255,0.22);
    padding: 2.5rem;
    border-radius: 20px;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}
button[kind="primary"] {
    background: linear-gradient(90deg, #d53369 0%, #daae51 100%) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.2rem !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# OPENAI CLIENT
# ---------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# ---------------------------------
# MAIN TITLE
# ---------------------------------
st.title("✨ StudyGenie – Your K-Drama Style AI Bestie 💗")
st.write("Ask doubts, generate notes, summaries, timetables… or get a huge motivation push 😭🔥")

# Sidebar
st.sidebar.header("✨ Tools Menu")
tool = st.sidebar.selectbox(
    "Choose a feature",
    ["AI Doubt Solver", "Notes Generator", "Summary Maker", "Timetable Builder", "Motivation Booster"]
)

# ---------------------------------
# AI DOUBT SOLVER (FULLY WORKING)
# ---------------------------------
if tool == "AI Doubt Solver":
    st.subheader("💡 Ask me anything bestie, I got you:")
    question = st.text_area("Write your doubt here:")

    if st.button("Solve My Doubt"):
        if question.strip():

            with st.spinner("Thinking for you babe… 💭✨"):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are StudyGenie, a friendly smart AI study partner."},
                        {"role": "user", "content": question}
                    ]
                )

            st.success("Here you go bestie 💗👇")
            st.write(response.choices[0].message["content"])

        else:
            st.warning("Write your question first bestie 😭")

# ---------------------------------
# NOTES GENERATOR
# ---------------------------------
elif tool == "Notes Generator":
    st.subheader("📝 Generate aesthetic notes")
    topic = st.text_input("Topic name:")

    if st.button("Generate Notes"):
        if topic.strip():

            with st.spinner("Writing cute notes for you 💗📚…"):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Create short, clear, aesthetic study notes."},
                        {"role": "user", "content": f"Make notes on {topic}"}
                    ]
                )
            st.success("Your Notes ✨")
            st.write(response.choices[0].message["content"])

        else:
            st.warning("Topic daal do bestie 😭")

# ---------------------------------
# SUMMARY MAKER
# ---------------------------------
elif tool == "Summary Maker":
    st.subheader("📄 Summaries in seconds")
    text = st.text_area("Paste the paragraph:")

    if st.button("Summarize"):
        if text.strip():

            with st.spinner("Summarizing for you 💞"):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Summarize text in simple short points."},
                        {"role": "user", "content": text}
                    ]
                )

            st.success("Your Summary ✨")
            st.write(response.choices[0].message["content"])

        else:
            st.warning("Paste something bestie 🥺")

# ---------------------------------
# TIMETABLE BUILDER
# ---------------------------------
elif tool == "Timetable Builder":
    st.subheader("📅 Build your aesthetic timetable")
    subjects = st.text_input("Enter subjects (comma separated):")
    hours = st.slider("Daily Study Hours", 1, 12, 4)

    if st.button("Create Timetable"):
        if subjects.strip():
            list_subjects = [i.strip() for i in subjects.split(",")]
            time_each = round(hours / len(list_subjects), 2)

            st.success("Your Timetable 💗")
            for s in list_subjects:
                st.write(f"✨ **{s}** – {time_each} hrs")

        else:
            st.warning("Add at least one subject 😭")

# ---------------------------------
# MOTIVATION BOOSTER
# ---------------------------------
elif tool == "Motivation Booster":
    st.subheader("🔥 Ready for giga-level motivation?")
    
    quotes = [
        "Bestie you’re literally the future millionaire of your family 💗🔥",
        "Korea is waiting for you babe—keep moving 😭✨",
        "Your glow-up is uploading… do NOT cancel the download 😤🔥",
        "Study now, flex forever. That’s the vibe 💅✨",
        "You have no idea how powerful you actually are 🌟",
        "Every minute you study adds +1 charm to your aura 😭💗",
        "You’re not tired, you’re leveling up 🔮✨",
        "Your dream life is not far—it’s IN PROGRESS 🔥",
        "The world is NOT ready for your next version 😭💞",
        "One day, you’ll be living the life you prayed for.",
        "Focus now, because your future is screaming your name 🔥✨",
        "Nobody has your mind, your vibe, your ambition 💗",
        "You are not average. Stop acting like it 😤🔥",
        "Small steps → Big changes. Keep going bestie ✨",
        "You’re the main character. Everyone else is extra 😎",
        "Your future self is literally cheering rn 😭💗",
        "You are meant for greatness—own it 🦋",
        "Discipline looks sexy on you bestie 🔥",
        "Your success arc is about to EXPLODE 💥",
        "Babe… you’re unstoppable. Trust me 💗",
        "Every time you choose discipline, you win.",
        "Don’t stop. Your best chapter isn’t written yet ✨",
        "Glow-up incoming. Don’t blink 😤🔥",
        "You’re building a life people dream about 💞",
        "One hour today → One dream tomorrow 💙",
        "Bestie your potential is insane. USE IT 🔥",
        "Imagine quitting now? Couldn’t be you 😭🔥",
    ]

    if st.button("Boost Me"):
        st.success(random.choice(quotes))