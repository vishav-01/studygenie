import streamlit as st import requests import random

------------------------------------

PAGE CONFIG

------------------------------------

st.set_page_config(page_title="StudyGenie", page_icon="📚", layout="centered")

------------------------------------

BACKGROUND GRADIENT (LIGHT KDRAMA VIBES)

------------------------------------

st.markdown( """ <style> body { background: linear-gradient(135deg, #ffe8ff, #e3d7ff, #d6f1ff); background-size: 400% 400%; animation: gradientMove 8s ease infinite; font-family: 'Poppins', sans-serif; }

@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.kiss-anim {
    animation: pop 0.4s ease;
}

@keyframes pop {
    0% {transform: scale(0.8); opacity: 0;}
    100% {transform: scale(1); opacity: 1;}
}
</style>
""",
unsafe_allow_html=True,

)

------------------------------------

HEADER

------------------------------------

st.markdown("<h1 class='kiss-anim' style='text-align:center;'>📚 StudyGenie – Your AI Study Bestie 💗✨</h1>", unsafe_allow_html=True) st.write("Ask doubts, generate notes, summaries, timetables and boost your motivation ✨")

------------------------------------

OPENAI SAFE REQUEST FUNCTION

------------------------------------

def ask_openai(prompt): try: response = requests.post( "https://api.openai.com/v1/chat/completions", headers={ "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}", "Content-Type": "application/json" }, json={ "model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}] } )

json_res = response.json()

    # If OpenAI returns error
    if "error" in json_res:
        return "❌ AI Error: " + json_res["error"]["message"]

    # If response does not contain 'choices'
    if "choices" not in json_res:
        return "❌ AI didn't respond properly. Try again bestie 💗"

    return json_res["choices"][0]["message"]["content"]

except Exception as e:
    return f"❌ Connection Error: {e}"

------------------------------------

SIDEBAR NAVIGATION

------------------------------------

tool = st.sidebar.selectbox( "Choose your tool", [ "AI Doubt Solver", "Notes Generator", "Summary Maker", "Timetable Builder", "Motivation Booster" ] )

------------------------------------

TOOL: AI DOUBT SOLVER

------------------------------------

if tool == "AI Doubt Solver": st.subheader("💡 Ask any academic doubt") q = st.text_area("Type your question:")

if st.button("Solve ✨"):
    if q.strip():
        reply = ask_openai(q)
        st.success(reply)
    else:
        st.warning("Type something first bestie 💗")

------------------------------------

TOOL: NOTES GENERATOR

------------------------------------

elif tool == "Notes Generator": st.subheader("📝 Generate neat notes") topic = st.text_input("Enter topic name")

if st.button("Generate Notes ✨"):
    if topic.strip():
        prompt = f"Make clean CBSE Class 11 style notes on: {topic}"
        reply = ask_openai(prompt)
        st.success(reply)
    else:
        st.warning("Enter a topic first 💗")

------------------------------------

SUMMARY MAKER

------------------------------------

elif tool == "Summary Maker": st.subheader("📄 Make short summary") para = st.text_area("Paste your paragraph")

if st.button("Summarize ✨"):
    if para.strip():
        prompt = f"Summarize this in simple points: {para}"
        reply = ask_openai(prompt)
        st.success(reply)
    else:
        st.warning("Paste something first 💗")

------------------------------------

TIMETABLE BUILDER

------------------------------------

elif tool == "Timetable Builder": st.subheader("📅 Create study timetable") subjects = st.text_input("Subjects (comma separated)") hrs = st.slider("Study hours/day", 1, 12, 4)

if st.button("Build Timetable ✨"):
    if subjects.strip():
        list_sub = [s.strip() for s in subjects.split(",")]
        each = round(hrs / len(list_sub), 2)

        st.success("Your Timetable 💗")
        for s in list_sub:
            st.write(f"• {s}: {each} hrs")
    else:
        st.warning("Enter at least one subject 💗")

------------------------------------

MOTIVATION BOOSTER

------------------------------------

elif tool == "Motivation Booster": st.subheader("🔥 Boost Mode Activated") quotes = [ "Bestie you got this 😭🔥", "You’re literally becoming your dream person 💗", "Glow up in progress, don’t interrupt ✨", "Future you is flexing because of present you 💅", "You are unstoppable, babe 🔥", "Focus now, luxury life later 💸", "You're smarter than you think, cuter than you know 💗", "One chapter a day = a whole new future 📚", "You’re the main character, act like it ✨", "Every effort you make is building your dream life 💕", "Discipline = glow up fuel ✨", "You’re destined for something BIG, trust me 💗", "Small steps > No steps 🔥", "You're doing better than you think bestie 💕", "Study hard, shine harder ✨", "Success is already looking at you babe 😤🔥", "You are not behind, you're just charging up ⚡", "Dream big, work quietly, flex loudly later 😎", "Bestie your future apartment in Seoul is waiting 💗", "You’re building a version of yourself you’ll be proud of 💕", "Never forget: you're THAT guy 😤🔥", "You deserve the life you're dreaming of ✨", "Keep going, your breakthrough is loading… 💗", "Your study era = glow era ✨", "One day your hard work will shock everybody 😭🔥", "Let them sleep, you grind, you win 💕" ]

if st.button("Boost Me ✨"):
    st.success(random.choice(quotes))