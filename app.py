import streamlit as st
from openai import OpenAI

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="StudyGenie – AI Bestie",
    page_icon="✨",
    layout="centered"
)

# ---------------- CSS (Visible Gradient, No Animations) ----------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    * {
        font-family: 'Poppins', sans-serif !important;
    }

    body {
        background: linear-gradient(135deg, #6C63FF, #A35BFF, #FF69B4);
        background-size: cover;
    }

    .glass-box {
        background: rgba(255,255,255,0.15);
        padding: 20px;
        border-radius: 18px;
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.25);
        color: white;
        margin-top: 10px;
    }

    textarea, input {
        background: rgba(255,255,255,0.25) !important;
        color: white !important;
    }

    .stButton>button {
        background: #ffffff33;
        border-radius: 12px;
        border: 1px solid #ffffff77;
        color: white;
        font-weight: 600;
        padding: 8px 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center; color:white;'>📚 StudyGenie – Your AI Bestie 💗</h1>", unsafe_allow_html=True)
st.write("<p style='text-align:center; color:white;'>Ask doubts, make notes, summaries, timetables – anything bestie 😭✨</p>", unsafe_allow_html=True)

# ---------------- OPENAI API KEY ----------------
with st.sidebar:
    st.header("🔑 API Settings")
    api_key = st.text_input("Enter OpenAI API Key:", type="password")

# ---------------- TOOLS SIDEBAR ----------------
st.sidebar.header("✨ Tools")
tool = st.sidebar.selectbox(
    "Choose a feature",
    ["AI Doubt Solver", "Notes Generator", "Summary Maker", "Timetable Builder", "Motivation Booster"]
)

# ---------------- OPENAI FUNCTION ----------------
def ask_openai(question):
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content
    except:
        return "API error bestie 😭. Check your key."

# ---------------- FEATURES ----------------

# DOUBT SOLVER
if tool == "AI Doubt Solver":
    st.markdown("<div class='glass-box'>💡 Ask any doubt</div>", unsafe_allow_html=True)
    q = st.text_area("Type your question here:")

    if st.button("Solve ✨"):
        if not api_key:
            st.error("Enter your OpenAI API key bestie 😭")
        elif q.strip():
            st.success("✨ Answer:")
            st.write(ask_openai(q))
        else:
            st.warning("Type something first babe 😭")


# NOTES GENERATOR
elif tool == "Notes Generator":
    st.markdown("<div class='glass-box'>📝 Notes Generator</div>", unsafe_allow_html=True)
    topic = st.text_input("Enter topic:")

    if st.button("Generate Notes"):
        if not api_key:
            st.error("Enter your OpenAI API key bestie 😭")
        elif topic.strip():
            st.success("✨ Notes:")
            st.write(ask_openai(f"Make student-friendly notes on {topic}"))
        else:
            st.warning("Type a topic first!")


# SUMMARY MAKER
elif tool == "Summary Maker":
    st.markdown("<div class='glass-box'>📄 Summary Maker</div>", unsafe_allow_html=True)
    text = st.text_area("Paste a paragraph:")

    if st.button("Summarize ✂️"):
        if not api_key:
            st.error("Enter API key bestie 😭")
        elif text.strip():
            st.success("✨ Summary:")
            st.write(ask_openai(f"Summarize this clearly:\n{text}"))
        else:
            st.warning("Paste something first!")


# TIMETABLE BUILDER
elif tool == "Timetable Builder":
    st.markdown("<div class='glass-box'>📅 Timetable Builder</div>", unsafe_allow_html=True)
    subjects = st.text_input("Subjects (comma separated):")
    hours = st.slider("Study hours/day", 1, 12, 4)

    if st.button("Create Timetable"):
        if subjects.strip():
            names = [s.strip() for s in subjects.split(",")]
            time = round(hours / len(names), 2)
            st.success("✨ Your Timetable")
            for s in names:
                st.write(f"• **{s}:** {time} hrs")
        else:
            st.warning("Enter subjects first!")


# MOTIVATION BOOSTER
elif tool == "Motivation Booster":
    st.markdown("<div class='glass-box'>🔥 Motivation Booster</div>", unsafe_allow_html=True)

    quotes = [
        "Bestie you got this 😭🔥",
        "Study now, glow later ✨",
        "Your success arc is beginning 💗",
        "Focus now, flex forever 😤",
        "You’re literally unstoppable babe 💜",
        "One year of discipline = entire life changed.",
        "Imagine your future self hugging you rn 😭",
        "You're the main character, act like it ⭐",
        "Your Korean student era is loading 💗🇰🇷",
        "You're powerful. Even on bad days.",
        "Your dream life needs your 2025 grind.",
        "Stay consistent babe — magic is coming ✨",
        "Your haters check your progress daily 😂🔥",
        "Do it for your aesthetic future self 💗",
        "If you don’t give up, you win 🤍"
    ]

    import random
    if st.button("Boost Me ✨"):
        st.success(random.choice(quotes))