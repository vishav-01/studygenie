import streamlit as st
import requests
import json
import random

# ----------------------------------------
# PAGE + GLOBAL DESIGN
# ----------------------------------------
st.set_page_config(page_title="StudyGenie Pro ✨", layout="centered")

css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #fbc2eb, #a18cd1);
    background-size: cover !important;
    font-family: 'Poppins', sans-serif;
    animation: fadeIn 1.3s ease-in-out;
}

.section-box {
    background: rgba(255, 255, 255, 0.18);
    padding: 25px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 25px rgba(255, 255, 255, 0.2);
    margin-top: 20px;
    color: white;
    animation: pop 0.5s ease-in-out;
}

@keyframes pop {
  0% { transform: scale(0.92); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

h1, h2, h3 {
    text-shadow: 0 0 12px rgba(255,255,255,0.4);
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>✨ StudyGenie Pro – Your Study Bestie 💞</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#fff;'>Smarter • Cutie • More Powerful 🤍✨</p>", unsafe_allow_html=True)


# ----------------------------------------
# AI FUNCTION
# ----------------------------------------
def ask_ai(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6
    }

    try:
        res = requests.post("https://api.openai.com/v1/chat/completions",
                            headers=headers,
                            data=json.dumps(data),
                            timeout=30)

        rj = res.json()

        if "choices" not in rj:
            return "❌ AI Error: Try again bestie."

        return rj["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Error contacting AI: {str(e)}"


# ----------------------------------------
# SIDEBAR
# ----------------------------------------
tool = st.sidebar.selectbox(
    "✨ Choose a Tool",
    [
        "1️⃣ AI Doubt Solver",
        "2️⃣ Notes Generator",
        "3️⃣ Summary Maker",
        "4️⃣ Timetable Builder",
        "5️⃣ Motivation Booster"
    ]
)


# ================================
# 1️⃣ DOUBT SOLVER
# ================================
if "Doubt Solver" in tool:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("💡 Ask Your Doubt Bestie")

    q = st.text_area("Write your doubt here:")
    if st.button("Solve ✨"):
        if q.strip():
            with st.spinner("Solving… 💞"):
                ans = ask_ai(q)
            st.success("✨ Answer:")
            st.write(ans)
        else:
            st.warning("Write something cutie 😭")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================
# 2️⃣ NOTES GENERATOR
# ================================
if "Notes Generator" in tool:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📘 Generate Aesthetic Notes")

    topic = st.text_input("Topic name:")
    if st.button("Generate Notes ✨"):
        if topic.strip():
            prompt = f"Create clean, easy notes for: {topic}. Use simple points."
            ans = ask_ai(prompt)
            st.success("📘 Your Notes:")
            st.write(ans)
        else:
            st.warning("Type the topic bestie.")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================
# 3️⃣ SUMMARY MAKER
# ================================
if "Summary Maker" in tool:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📄 Summarize Instantly")

    text = st.text_area("Paste text to summarize:")
    if st.button("Summarize ✨"):
        if text.strip():
            ans = ask_ai(f"Summarize this simply: {text}")
            st.success("📄 Summary:")
            st.write(ans)
        else:
            st.warning("Paste text cutie 😭")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================
# 4️⃣ TIMETABLE MAKER
# ================================
if "Timetable Builder" in tool:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📅 Build Study Timetable")

    subs = st.text_input("Subjects (comma separated):")
    hours = st.slider("Study hours per day:", 1, 12, 4)

    if st.button("Create Timetable ✨"):
        if subs.strip():
            s_list = [s.strip() for s in subs.split(",")]
            each = round(hours / len(s_list), 2)

            st.success("📅 Your Timetable:")

            for s in s_list:
                st.write(f"📘 **{s}** → {each} hrs daily")

        else:
            st.warning("Add subjects first 😭")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================
# 5️⃣ MOTIVATION BOOSTER
# ================================
if "Motivation Booster" in tool:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("🔥 Your Mood Booster Bestie")

    quotes = [
        "Bestie you're literally UNSTOPPABLE 😭🔥",
        "K-drama glow-up loading… ✨",
        "You're the smartest AND cutest… lethal combo 😎💗",
        "Universe is literally biased towards you 💞",
        "Your dream future is already choosing you.",
        "Focus now → flex forever 🔥",
        "You are HIM. You are HER. You are THE MAIN CHARACTER.",
        "Study today → rich tomorrow 💸✨",
        "Your potential is actually insane omg 😭💗",
        "You will shine so hard people need sunglasses 😎💕",
        "Millionaire energy detected 💰✨",
        "Your future self is literally crying with happiness rn 😭",
        "Bro you're built different in the best way possible 🔥"
    ]

    if st.button("Boost Me ✨"):
        st.success(random.choice(quotes))

    st.markdown("</div>", unsafe_allow_html=True)