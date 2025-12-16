import streamlit as st
import requests, json, random

# ================= PAGE CONFIG =================
st.set_page_config("StudyGenie AI", layout="wide")

# ================= THEME =================
theme = st.sidebar.selectbox(
    "🌈 Choose Theme",
    ["Sky Blue", "Pink Pastel", "Lavender"]
)

themes = {
    "Sky Blue": ("#e8f4ff", "#cce4ff"),
    "Pink Pastel": ("#ffe6f2", "#fdd1e8"),
    "Lavender": ("#f0e9ff", "#e2d6ff")
}
g1, g2 = themes[theme]

st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(180deg, {g1}, {g2});
    font-family: 'Poppins', sans-serif;
}}
.section {{
    background: rgba(255,255,255,0.55);
    padding: 25px;
    border-radius: 20px;
    max-width: 700px;
    margin: auto;
}}
.genie {{
    background: white;
    padding: 16px;
    margin-top: 15px;
    border-radius: 15px;
    border-left: 4px solid #9b7cff;
}}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<h1 style="text-align:center;">✨ StudyGenie AI – Your Personal AI Study Bestie 💕</h1>
<p style="text-align:center;">Always here for your doubts, dreams & glow-up ✨</p>
""", unsafe_allow_html=True)

# ================= AI CALL =================
def ask_ai(prompt):
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4.1-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6,
        "max_tokens": 1500
    }
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload)
    )
    return r.json()["choices"][0]["message"]["content"]

# ================= SIDEBAR =================
tool = st.sidebar.radio(
    "✨ Choose your tool",
    [
        "AI Planner",
        "Mindset Reset",
        "Study Routine Designer",
        "Exam Strategy Maker",
        "Personal Study Coach",
        "Mini IQ Test 🧠"
    ]
)

# ================= AI PLANNER =================
if tool == "AI Planner":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("📆 Daily Study Planner")

    goal = st.text_input("Your goal:")

    if st.button("Make Plan ✨"):
        res = ask_ai(f"Create a simple daily study plan for: {goal}")
        st.markdown(f"<div class='genie'>{res}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================= MINDSET RESET =================
elif tool == "Mindset Reset":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🌸 Mindset Reset")

    if st.button("Reset My Mind ✨"):
        res = ask_ai("Give a calm, motivating mindset reset.")
        st.markdown(f"<div class='genie'>{res}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================= STUDY ROUTINE =================
elif tool == "Study Routine Designer":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("📚 Study Routine Designer")

    hrs = st.slider("How many hours can you study daily?", 1, 10, 4)

    if st.button("Design Routine ✨"):
        res = ask_ai(f"Design a clean study routine for {hrs} hours.")
        st.markdown(f"<div class='genie'>{res}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================= EXAM STRATEGY =================
elif tool == "Exam Strategy Maker":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🎯 Exam Strategy")

    exam = st.text_input("Your exam:")

    if st.button("Build Strategy ✨"):
        res = ask_ai(f"Create a high-impact exam strategy for {exam}")
        st.markdown(f"<div class='genie'>{res}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================= STUDY COACH =================
elif tool == "Personal Study Coach":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("💞 Personal Study Coach")

    prob = st.text_area("Tell me what you're struggling with:")

    if st.button("Coach Me ✨"):
        res = ask_ai(f"You are a kind personal study coach. Help with: {prob}")
        st.markdown(f"<div class='genie'>{res}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================= IQ GAME (100+ READY) =================
elif tool == "Mini IQ Test 🧠":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🧠 Mini IQ Test")

    iq_questions = [
        ("2, 6, 12, 20, ?", ["30", "28", "24", "36"], "30"),
        ("A, D, G, J, ?", ["M", "K", "L", "N"], "M"),
        ("Which is odd?", ["125", "64", "27", "144"], "144"),
        # 👉 ADD UP TO 100+ SAME FORMAT
    ]

    if "q" not in st.session_state:
        st.session_state.q = random.choice(iq_questions)

    q, opt, ans = st.session_state.q
    st.markdown(f"<div class='genie'><b>{q}</b></div>", unsafe_allow_html=True)

    choice = st.radio("Choose:", opt)

    if st.button("Submit"):
        if choice == ans:
            st.success("🔥 Correct! High-IQ detected")
        else:
            st.error(f"❌ Correct answer: {ans}")

    if st.button("Next Question"):
        st.session_state.q = random.choice(iq_questions)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)