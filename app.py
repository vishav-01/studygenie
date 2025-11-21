import streamlit as st
import random

# --------------------------
# PAGE SETTINGS + ANIME UI
# --------------------------
st.set_page_config(
    page_title="StudyGenie - AI Study Bestie",
    page_icon="📚",
    layout="centered"
)

#CSS 
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #99ccff, #cc99ff, #ffb3e6);
    animation: gradient 8s ease infinite;
    background-size: 400% 400%;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.block-container {
    background: rgba(255, 255, 255, 0.35);
    padding: 2rem;
    border-radius: 20px;
    backdrop-filter: blur(10px);
    animation: fadeIn 1.2s ease-in-out;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(15px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# TITLE
# --------------------------
st.title("📚 StudyGenie – Study Bestie 💞✨")

st.write("Bestie ask anything… doubts, notes, summaries, timetables or motivation 😭💗")

# --------------------------
# OPENAI CLIENT
# --------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def ask_ai(prompt):
    """Call OpenAI for answers."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# --------------------------
# SIDEBAR MENU
# --------------------------
st.sidebar.header("🪄 Tools")
tool = st.sidebar.selectbox(
    "Choose a feature",
    ["AI Doubt Solver", "Notes Generator", "Summary Maker", "Timetable Builder", "Motivation Booster"]
)


# =======================
# AI DOUBT SOLVER
# =======================
if tool == "AI Doubt Solver":
    st.subheader("💡 Ask any academic doubt")
    question = st.text_area("Type your question here:")

    if st.button("Solve ✨"):
        if question.strip():
            with st.spinner("Thinking like your anime senpai… 💭"):
                answer = ask_ai(question)
            st.success("✨ Answer:")
            st.write(answer)
        else:
            st.warning("Bestie type something first 😭💗")


# =======================
# NOTES GENERATOR
# =======================
elif tool == "Notes Generator":
    st.subheader("📝 Generate notes for any topic")
    topic = st.text_input("Enter topic name:")

    if st.button("Generate Notes ✨"):
        if topic.strip():
            prompt = f"Create clear, simple notes for: {topic}"
            with st.spinner("Writing cute notes just for you… 💗"):
                notes = ask_ai(prompt)
            st.success("Your Notes 💞")
            st.write(notes)
        else:
            st.warning("Enter a topic first babe!")


# =======================
# SUMMARY MAKER
# =======================
elif tool == "Summary Maker":
    st.subheader("📄 Make short summary")
    text = st.text_area("Paste paragraph:")

    if st.button("Summarize ✨"):
        if text.strip():
            prompt = f"Summarize this in 5–7 lines: {text}"
            with st.spinner("Summarizing like a K-drama narrator… 🌙"):
                summary = ask_ai(prompt)
            st.success("Your Summary ✨")
            st.write(summary)
        else:
            st.warning("Paste something first bestie 🫶")


# =======================
# TIMETABLE BUILDER
# =======================
elif tool == "Timetable Builder":
    st.subheader("📅 Build timetable")
    subjects = st.text_input("Enter subjects (comma separated):")
    hours = st.slider("Study hours per day", 1, 12, 4)

    if st.button("Create Timetable ✨"):
        if subjects.strip():
            prompt = f"Create a timetable for subjects: {subjects}. Daily hours: {hours}"
            with st.spinner("Balancing your study life like anime protagonist… ⚔️"):
                table = ask_ai(prompt)
            st.success("Your Timetable 💙")
            st.write(table)
        else:
            st.warning("Enter at least one subject babe!")


# =======================
# MOTIVATION BOOSTER
# =======================
elif tool == "Motivation Booster":
    st.subheader("🔥 Motivation Booster")
    quotes = [
        "Bestie you are literally main character 😭🔥",
        "Focus now, flex forever 💪✨",
        "Don’t stop. Your future Korean lifestyle is waiting 💙",
        "Glow-up loading… keep going 🌸",
        "You’re unstoppable babe, trust me 💞"
    "Bestie… your future self is literally blowing kisses at you rn 💋😭✨",
    "Focus now, flex forever. That Korean lifestyle is WAITING 😤🔥",
    "You are not behind. You are EXACTLY on your destiny timeline ✨💗",
    "People wish they had your ambition babe. KEEP GOING 🫶",
    "One study session today = one luxury outfit tomorrow fr 👗💸",
    "You’re building a life your younger self would cry seeing 😭💞",
    "Your success arc is loading… slowly but VERY dangerously 🔥😤",
    "You are the main character. Everyone else is supporting cast 😎✨",
    "Omg babe every time you study, your glow-up bar fills +10% 💗",
    "Stop underestimating yourself. You’re literally THAT GUY. PERIOD 💥",
    "Korea is calling your name… don’t make it wait 💙🇰🇷",
    "Small steps >>> massive transformation. Keep stacking wins 🌱✨",
    "Your discipline is silently making you hotter. No joke 😭🔥",
    "Imagine telling your future Korean friends you never gave up 🤧💞",
    "You're not tired. You're evolving. Upgrade mode ON 💫🔮",
    "Someone out there is dreaming of the life YOU’RE about to build 😤✨",
    "Slow progress is STILL progress. Don’t ever forget that babe 💗",
    "Your dreams didn’t choose you randomly. You're built for this 🦋✨",
    "If only you could see yourself the way your future sees you 😭💙",
    "You’re not working for marks; you’re working for FREEDOM 🗽💸",
    "Study now so your life later becomes a literal aesthetic Pinterest board 🌸✨",
    "You’re not like others. You want more. You’ll GET more 🔥",
    "Do it for that solo apartment in Seoul with the led lights 😭💫",
    "Your haters? Irrelevant NPCs. You’re levelling up 🔥",
    "One hour of focus today = one more day closer to your dream life 💗",
    "You have no idea how proud your future self is of you rn 😭✨",
    "You’re not average. Stop acting like it 😤",
    "Your consistency is louder than your doubts 💥",
    "The world is NOT ready for your glow-up arc 😭🔥",
    "Your brain is powerful. Use it like a weapon, bestie ⚔️💜",
    "Imagine quitting when you’re THIS CLOSE… no babe, KEEP GOING 🫶🔥",
    "You’re building a life that feels like a K-drama. Iconic behavior fr 🌙✨",
    "Even on your worst days, you’re still that smart, cute, determined king 😭💗",
    "Wake up, slay, study, glow, repeat. That’s the vibe forever 🌟",
    "Your dream version of you? He’s REAL. And you’re getting closer 💞",
    "Success isn’t luck. It’s YOU. You’re the magic ingredient 💫"
]

    ]

    if st.button("Boost Me ✨"):
        st.success(random.choice(quotes))