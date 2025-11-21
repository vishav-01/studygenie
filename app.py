# app.py - StudyGenie Pro v2 (Full Features)
import streamlit as st
import requests
import json
import random
import time
from io import BytesIO

# ------------------ CONFIG ------------------
st.set_page_config(page_title="StudyGenie Pro v2", page_icon="✨", layout="centered")

# ------------------ THEME / CSS ------------------
def inject_css(dark_mode=False):
    if dark_mode:
        bg = "linear-gradient(180deg, #0f172a, #1f2a44, #2b2540)"
        card_bg = "rgba(255,255,255,0.04)"
        text_color = "#e6e6ff"
    else:
        bg = "linear-gradient(180deg, #fef3ff, #e9d5ff, #e0f2fe)"
        card_bg = "rgba(255,255,255,0.6)"
        text_color = "#1f1730"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        background: {bg};
        background-attachment: fixed;
        font-family: 'Poppins', sans-serif;
        color: {text_color};
    }}

    .card {{
        background: {card_bg};
        padding: 18px;
        border-radius: 14px;
        backdrop-filter: blur(8px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        margin-bottom: 14px;
    }}

    .wide {{
        max-width: 1100px;
        margin-left: auto;
        margin-right: auto;
    }}

    .btn {{
        border-radius: 12px;
    }}

    /* simple spinner */
    .spinner {{
      border: 6px solid rgba(255,255,255,0.15);
      border-top: 6px solid rgba(255,255,255,0.9);
      border-radius: 50%;
      width: 36px;
      height: 36px;
      animation: spin 0.9s linear infinite;
      margin: auto;
    }}
    @keyframes spin {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Dark mode toggle stored in session
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ------------------ STATE SETUP ------------------
if "notes_store" not in st.session_state:
    st.session_state.notes_store = []  # list of dicts {title, content}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (role, text)
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []  # list of {q,a}
if "planner" not in st.session_state:
    st.session_state.planner = []  # list of tasks
if "profile" not in st.session_state:
    st.session_state.profile = {"name": "", "grade": "", "goal": ""}
if "last_ai_request" not in st.session_state:
    st.session_state.last_ai_request = None

inject_css(st.session_state.dark_mode)

# ------------------ HEADER ------------------
st.markdown("<div class='wide'>", unsafe_allow_html=True)
col1, col2 = st.columns([3,1])
with col1:
    st.markdown("<h1 style='margin:6px;'>📚 StudyGenie Pro v2</h1>", unsafe_allow_html=True)
    st.markdown("<div style='color:rgba(255,255,255,0.8)'>Your AI study bestie — flashcards, planner, brain-cleaner & more.</div>", unsafe_allow_html=True)
with col2:
    # Dark mode toggle
    if st.button("🌙 Dark Mode" if not st.session_state.dark_mode else "🌤️ Light Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        inject_css(st.session_state.dark_mode)
st.markdown("</div>", unsafe_allow_html=True)

# ------------------ SIDEBAR SETTINGS / NAV ------------------
st.sidebar.header("StudyGenie Controls")
with st.sidebar.expander("OpenAI key (Secrets recommended)"):
    st.markdown("Add your `OPENAI_API_KEY` to Streamlit Secrets for safety.")
st.sidebar.write("Quick jump:")
feature = st.sidebar.radio("Go to", [
    "Home", "AI Doubt Solver", "Flashcards", "Notes", "Summary (Brain-Dump Cleaner)",
    "Answer Checker", "Planner", "Voice Input", "Profile", "Saved Notes"
])

# ------------------ HELPER: ROBUST OPENAI CALL ------------------
def ask_openai(prompt, model="gpt-4o-mini", temperature=0.45):
    # Prevent duplicate calls for same prompt (simple caching via session)
    if st.session_state.last_ai_request == prompt and prompt.strip():
        return "⚠️ Duplicate request blocked — please modify your prompt or press a different tool."

    key = st.secrets.get("OPENAI_API_KEY")
    if not key:
        return "❌ No API key found. Add OPENAI_API_KEY in Streamlit Secrets."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    data = {
        "model": model,
        "messages": [
            {"role":"system", "content": "You are StudyGenie — concise, friendly, helpful study assistant."},
            {"role":"user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 700
    }
    try:
        res = requests.post("https://api.openai.com/v1/chat/completions",
                            headers=headers,
                            data=json.dumps(data),
                            timeout=30)
    except Exception as e:
        return f"❌ Network error: {e}"

    try:
        rj = res.json()
    except Exception as e:
        return f"❌ Invalid JSON response: {e}"

    # safe handling
    if "error" in rj:
        return f"❌ AI error: {rj['error'].get('message', str(rj['error']))}"
    if "choices" not in rj or not rj["choices"]:
        return "❌ AI didn't return a usable response. Try again."
    out = rj["choices"][0].get("message", {}).get("content", "")
    st.session_state.last_ai_request = prompt
    return out or "❌ Empty response from AI."

# ------------------ HOME (Quick Buttons to 5 features) ------------------
if feature == "Home":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("✨ Quick Access")
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("1️⃣ Doubt"):
        feature = "AI Doubt Solver"
    if c2.button("2️⃣ Flashcards"):
        feature = "Flashcards"
    if c3.button("3️⃣ Notes"):
        feature = "Notes"
    if c4.button("4️⃣ Planner"):
        feature = "Planner"
    if c5.button("5️⃣ Boost"):
        feature = "Motivation Booster"
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ AI DOUBT SOLVER ------------------
if feature == "AI Doubt Solver":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💡 AI Doubt Solver")
    user_q = st.text_area("Type your question:", key="doubt_q")
    if st.button("Solve Doubt ✨"):
        if user_q.strip():
            with st.spinner("Thinking..."):
                ans = ask_openai(user_q)
            st.success("Answer:")
            st.write(ans)
            st.session_state.chat_history.append(("user", user_q))
            st.session_state.chat_history.append(("ai", ans))
        else:
            st.warning("Ask something first!")
    # chat history viewer
    if st.checkbox("Show chat history"):
        for role, txt in st.session_state.chat_history[::-1]:
            badge = "You" if role == "user" else "StudyGenie"
            st.markdown(f"**{badge}:** {txt}")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ FLASHCARDS ------------------
elif feature == "Flashcards":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🃏 Flashcards — Generate & Study")
    fc_topic = st.text_input("Topic for flashcards:")
    fc_size = st.slider("How many cards?", 3, 20, 6)
    if st.button("Create Flashcards"):
        if fc_topic.strip():
            prompt = f"Create {fc_size} simple Q&A flashcards on: {fc_topic}. Return as numbered Q:... A:..."
            raw = ask_openai(prompt)
            # parse simple Q/A pairs
            cards = []
            lines = raw.splitlines()
            q, a = None, None
            for line in lines:
                line = line.strip()
                if line.lower().startswith("q:") or line.lower().startswith("question"):
                    q = line.split(":",1)[1].strip()
                elif line.lower().startswith("a:") or line.lower().startswith("answer"):
                    a = line.split(":",1)[1].strip()
                elif line and (q is None):
                    # fallback: try to split by " - "
                    pass
                if q and a:
                    cards.append({"q": q, "a": a})
                    q, a = None, None
            if not cards:
                # fallback: split by double newlines
                parts = raw.split("\n\n")
                for p in parts:
                    if ":" in p:
                        segs = p.split(":")
                        cards.append({"q": segs[0][:200].strip(), "a": ":".join(segs[1:]).strip()})
            st.session_state.flashcards = cards
            st.success(f"Created {len(cards)} cards.")
        else:
            st.warning("Enter topic first!")

    if st.session_state.flashcards:
        st.write("Study Mode:")
        idx = st.number_input("Card index", min_value=1, max_value=max(1, len(st.session_state.flashcards)), value=1)
        card = st.session_state.flashcards[int(idx)-1]
        st.markdown(f"**Q:** {card['q']}")
        if st.button("Show Answer"):
            st.markdown(f"**A:** {card['a']}")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ NOTES (Generate & Save) ------------------
elif feature == "Notes":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 Notes Generator & Save")
    note_topic = st.text_input("Topic for notes:")
    if st.button("Generate Notes"):
        if note_topic.strip():
            prompt = f"Create clear, concise CBSE Class 11 notes on: {note_topic}. Use bullet points and examples."
            with st.spinner("Writing notes..."):
                notes_out = ask_openai(prompt)
            st.text_area("Generated Notes", value=notes_out, height=260, key="gen_notes")
        else:
            st.warning("Enter a topic!")

    if st.session_state.get("gen_notes"):
        if st.button("Save Notes"):
            st.session_state.notes_store.append({"title": note_topic or "Untitled", "content": st.session_state.get("gen_notes")})
            st.success("Saved to your notes.")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ SUMMARY / BRAIN-DUMP CLEANER ------------------
elif feature == "Summary (Brain-Dump Cleaner)":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🧠 Brain-Dump Cleaner — Turn messy into neat")
    messy = st.text_area("Paste your messy notes / brain-dump here:")
    if st.button("Clean & Organize"):
        if messy.strip():
            prompt = f"Organize and clean this brain-dump into titled sections, bullet points, and action items:\n\n{messy}"
            with st.spinner("Cleaning your brain-dump..."):
                cleaned = ask_openai(prompt)
            st.success("Cleaned Output:")
            st.write(cleaned)
        else:
            st.warning("Paste something first!")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ ANSWER CHECKER ------------------
elif feature == "Answer Checker":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("✅ Answer Checker — Grade & Feedback")
    question = st.text_input("Question / Prompt:")
    student_answer = st.text_area("Student's Answer:")
    if st.button("Check Answer"):
        if question.strip() and student_answer.strip():
            prompt = f"Given the question:\n{question}\n\nEvaluate the student's answer:\n{student_answer}\n\nGive an overall score out of 10 and provide concise feedback on mistakes and improvements."
            with st.spinner("Checking..."):
                feedback = ask_openai(prompt)
            st.success("Feedback & Score:")
            st.write(feedback)
        else:
            st.warning("Add question and student's answer first.")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ PLANNER ------------------
elif feature == "Planner":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📆 Planner — Tasks & Study Plan")
    task = st.text_input("New Task (e.g. Revise Chapter 3):")
    deadline = st.text_input("Deadline / When (optional):")
    if st.button("Add Task"):
        if task.strip():
            st.session_state.planner.append({"task": task, "deadline": deadline})
            st.success("Task added.")
        else:
            st.warning("Enter a task.")

    if st.session_state.planner:
        st.write("Your Tasks:")
        for i, t in enumerate(st.session_state.planner, 1):
            st.write(f"{i}. {t['task']} — {t['deadline']}")
        if st.button("Generate 7-day study plan from tasks"):
            prompts = "Make a 7-day study plan using these tasks:\n" + "\n".join([f"- {p['task']} ({p['deadline']})" for p in st.session_state.planner])
            with st.spinner("Creating plan..."):
                plan = ask_openai(prompts)
            st.success("Study Plan:")
            st.write(plan)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ VOICE INPUT (file upload -> transcription) ------------------
elif feature == "Voice Input":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🎤 Voice Input (Upload audio to transcribe)")
    audio_file = st.file_uploader("Upload audio (mp3, m4a, wav)", type=["mp3", "m4a", "wav"])
    if audio_file:
        if st.button("Transcribe & Answer"):
            # call OpenAI transcription endpoint (multipart)
            key = st.secrets.get("OPENAI_API_KEY")
            if not key:
                st.error("Add OPENAI_API_KEY to secrets.")
            else:
                with st.spinner("Transcribing..."):
                    try:
                        files = {"file": (audio_file.name, audio_file.getvalue())}
                        data = {"model": "gpt-4o-transcribe"}  # or 'whisper-1' depending on API
                        headers = {"Authorization": f"Bearer {key}"}
                        resp = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=60)
                        rj = resp.json()
                        if "error" in rj:
                            st.error("Transcription error: " + str(rj["error"].get("message","")))
                        else:
                            text = rj.get("text", "")
                            st.success("Transcribed Text:")
                            st.write(text)
                            # optional: ask AI to answer based on transcription
                            ans = ask_openai("Answer this based on transcript:\n" + text)
                            st.markdown("**Answer based on audio:**")
                            st.write(ans)
                    except Exception as e:
                        st.error("Transcription failed: " + str(e))
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ PROFILE ------------------
elif feature == "Profile":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👤 Your Profile")
    nm = st.text_input("Name", value=st.session_state.profile.get("name",""))
    grade = st.text_input("Grade / Year", value=st.session_state.profile.get("grade",""))
    goal = st.text_input("Short Goal (ex: Study in Korea)", value=st.session_state.profile.get("goal",""))
    if st.button("Save Profile"):
        st.session_state.profile.update({"name": nm, "grade": grade, "goal": goal})
        st.success("Profile saved.")
    st.markdown(f"**Saved Profile:** {st.session_state.profile}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ SAVED NOTES (download) ------------------
elif feature == "Saved Notes":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💾 Saved Notes")
    if st.session_state.notes_store:
        for i, n in enumerate(st.session_state.notes_store, 1):
            with st.expander(f"{i}. {n['title']}"):
                st.write(n["content"])
                b = st.button(f"Download {i}", key=f"dl{i}")
                if b:
                    st.download_button(f"Download {n['title']}", n["content"], file_name=f"{n['title']}.txt")
        if st.button("Clear all saved notes"):
            st.session_state.notes_store = []
            st.success("Cleared.")
    else:
        st.info("No saved notes yet.")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ MOTIVATION BOOSTER (shortcut) ------------------
# accessible from sidebar quick jump
if feature == "Motivation Booster" or feature == "Home":
    pass  # already included in main navigation flow

# ------------------ FOOTER ------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;color:rgba(255,255,255,0.9)'>Made with ❤️ — StudyGenie Pro</div>", unsafe_allow_html=True)