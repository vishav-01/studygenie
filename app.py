import streamlit as st
import requests
import json
import random

# -------------------------------
# PAGE & BACKGROUND
# -------------------------------
st.set_page_config(page_title="StudyGenie", layout="centered")

bg_css = """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #b3e5fc, #e1bee7, #f8bbd0);
    background-size: cover !important;
    background-attachment: fixed !important;
    font-family: 'Poppins', sans-serif;
}
.section-box {
    background: rgba(255,255,255,0.35);
    padding: 20px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    color: #2d0a31;
    margin-top: 20px;
}
h1,h2,h3,h4 {
    font-weight: 700;
}
</style>
"""
st.markdown(bg_css, unsafe_allow_html=True)

# -------------------------------
# LOCAL LOGIN (NO FIREBASE)
# -------------------------------
if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    st.title("✨ Welcome to StudyGenie")
    name = st.text_input("Enter your name to continue 💗")

    if st.button("Continue"):
        if name.strip():
            st.session_state.username = name
            st.rerun()
    st.stop()

# -------------------------------
# LOCAL CHAT HISTORY
# -------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------------
# OPENAI FUNCTION
# -------------------------------
def ai_answer(prompt):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Reply in short, clean, crisp student notes style."},
                {"role": "user", "content": prompt}
            ]
        }

        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )

        j = res.json()

        if "choices" not in j:
            return "AI Response Invalid ❌ (Try again!)"

        return j["choices"][0]["message"]["content"]

    except Exception as e:
        return "❌ Network or API Error: " + str(e)

# -------------------------------
# HEADER
# -------------------------------
st.markdown(f"<h1 style='text-align:center;'>📚 StudyGenie – Hi {st.session_state.username} 💗</h1>",
            unsafe_allow_html=True)

tool = st.sidebar.selectbox(
    "Choose Feature",
    ["AI Doubt Solver", "Notes Generator", "Summary Maker",
     "Timetable Maker", "Motivation Booster", "Chat History"]
)

# -------------------------------
# AI DOUBT SOLVER
# -------------------------------
if tool == "AI Doubt Solver":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("💡 Solve your academic doubt")

    q = st.text_area("Type your doubt:")
    if st.button("Get Answer"):
        if q.strip():
            with st.spinner("Thinking…"):
                ans = ai_answer(q)

            st.success("✨ Answer:")
            st.write(ans)

            st.session_state.history.append(("You: " + q, "AI: " + ans))
        else:
            st.warning("Please write something!")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# NOTES GENERATOR
# -------------------------------
elif tool == "Notes Generator":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📝 Generate Notes")

    topic = st.text_input("Topic:")
    if st.button("Generate"):
        if topic.strip():
            ans = ai_answer(f"Give crisp, short notes on: {topic}")
            st.success("📝 Notes:")
            st.write(ans)
            st.session_state.history.append((topic, ans))
        else:
            st.warning("Enter a topic!")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# SUMMARY MAKER
# -------------------------------
elif tool == "Summary Maker":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📄 Summary Maker")

    txt = st.text_area("Paste text:")
    if st.button("Summarize"):
        if txt.strip():
            ans = ai_answer(f"Summarize this: {txt}")
            st.success("✨ Summary:")
            st.write(ans)
            st.session_state.history.append((txt, ans))
        else:
            st.warning("Paste something!")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# TIMETABLE MAKER
# -------------------------------
elif tool == "Timetable Maker":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📅 Timetable Maker")

    s = st.text_input("Subjects (comma separated):")
    h = st.slider("Total study hours", 1, 12, 4)

    if st.button("Make Timetable"):
        if s.strip():
            subjects = [i.strip() for i in s.split(",")]
            each = round(h / len(subjects), 2)

            st.success("✨ Your Timetable:")
            for x in subjects:
                st.write(f"📘 {x}: **{each} hrs**")
        else:
            st.warning("Add subjects!")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# MOTIVATION BOOSTER
# -------------------------------
elif tool == "Motivation Booster":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("🔥 Motivation Booster")

    quotes = [
        "You have unlimited potential and strength.",
        "Your hard work today is shaping a powerful tomorrow.",
        "You are capable, intelligent and destined for success.",
        "Your dream is valid, real and achievable.",
        "Every effort you make is taking you forward.",
        "Your goals are proud of the person you are becoming.",
        "Your study journey is admirable and inspiring.",
        "Your future self appreciates your dedication today.",
        "You deserve every good thing that is coming.",
        "You are building a life you will be proud of.",
        "You are becoming stronger, wiser and sharper.",
        "Every page you study rewrites your future beautifully.",
    ]

    if st.button("Give Motivation"):
        st.success(random.choice(quotes))

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# CHAT HISTORY
# -------------------------------
elif tool == "Chat History":
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("💬 Your Chat History")

    if len(st.session_state.history) == 0:
        st.write("No chats yet!")
    else:
        for u, a in st.session_state.history:
            st.write(f"🧑 {u}")
            st.write(f"🤖 {a}")
            st.write("---")

    st.markdown("</div>", unsafe_allow_html=True)