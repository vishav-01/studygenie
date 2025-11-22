import streamlit as st
import json
import os
import uuid
from datetime import datetime
from openai import OpenAI

# --------------------------
# OPENAI CLIENT (GPT-4.1-mini)
# --------------------------
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))

# --------------------------
# FILE PATHS
# --------------------------
USER_DB = "users.json"
CHAT_DB = "chat_history.json"
PROFILE_DB = "profiles.json"

# --------------------------
# LOAD / SAVE HELPERS
# --------------------------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

users = load_json(USER_DB, {})
chat_history = load_json(CHAT_DB, {})
profiles = load_json(PROFILE_DB, {})

# --------------------------
# THEME SYSTEM
# --------------------------
THEMES = {
    "Pastel Sky": {
        "bg": "#EAF6FF",
        "card": "#FFFFFF",
        "accent": "#A7C7E7",
        "text": "#1A1A1A",
    },
    "Baby Pink": {
        "bg": "#FFEAF4",
        "card": "#FFFFFF",
        "accent": "#FFB7D5",
        "text": "#1A1A1A",
    },
    "Lavender Dream": {
        "bg": "#F3E8FF",
        "card": "#FFFFFF",
        "accent": "#D6B8FF",
        "text": "#1A1A1A",
    },
    "Sakura Blossom": {
        "bg": "#FFE5EC",
        "card": "#FFFFFF",
        "accent": "#FF9EBB",
        "text": "#1A1A1A",
    },
    "Dark Mode": {
        "bg": "#0D0D0D",
        "card": "#1A1A1A",
        "accent": "#7A5FFF",
        "text": "#FFFFFF",
    },
}

# --------------------------
# LOGIN SYSTEM (LOCAL)
# --------------------------
def login_screen():
    st.title("🌸 StudyGenie Ultra — Login")

    choice = st.radio("Select", ["Login", "Create Account"])

    if choice == "Create Account":
        username = st.text_input("Create a username")
        password = st.text_input("Create a password", type="password")

        if st.button("Create"):
            if username in users:
                st.error("Username already exists.")
            else:
                users[username] = {"password": password}
                profiles[username] = {
                    "theme": "Pastel Sky",
                    "avatar_color": "#FFB7D5",
                }
                save_json(USER_DB, users)
                save_json(PROFILE_DB, profiles)
                st.success("Account created! Please login now.")

    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state.user = username
                st.success("Logged in!")
            else:
                st.error("Invalid username or password.")

# Run login if needed
if "user" not in st.session_state:
    login_screen()
    st.stop()

current_user = st.session_state.user
current_profile = profiles.get(current_user, {})
current_theme = THEMES.get(current_profile.get("theme", "Pastel Sky"))

# --------------------------------------
# CHAT HISTORY SYSTEM
# --------------------------------------
def get_user_history(username):
    if username not in chat_history:
        chat_history[username] = []
    return chat_history[username]

def add_to_history(username, role, message):
    if username not in chat_history:
        chat_history[username] = []
    chat_history[username].append({
        "role": role,
        "message": message,
        "time": str(datetime.now())
    })
    save_json(CHAT_DB, chat_history)

# --------------------------------------
# USER PROFILE PAGE
# --------------------------------------
def profile_page():
    st.subheader("💖 Your Profile")

    st.write("Username:", current_user)

    avatar_color = st.color_picker("Avatar Color", current_profile.get("avatar_color", "#FFB7D5"))
    theme_choice = st.selectbox("Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(current_profile.get("theme", "Pastel Sky")))

    if st.button("Save Profile"):
        profiles[current_user]["avatar_color"] = avatar_color
        profiles[current_user]["theme"] = theme_choice
        save_json(PROFILE_DB, profiles)
        st.success("Profile updated!")

# --------------------------------------
# CHAT HISTORY PAGE
# --------------------------------------
def chat_history_page():
    st.subheader("🕒 Your Chat History")

    history = get_user_history(current_user)

    if not history:
        st.info("No chat history yet.")
        return

    for h in history:
        with st.container():
            st.markdown(
                f"""
                <div style='padding:10px; border-radius:12px; background:{current_theme['card']}; margin-bottom:8px;'>
                    <b style='color:{current_theme['accent']};'>{h['role'].upper()}</b><br>
                    <span style='color:{current_theme['text']};'>{h['message']}</span><br>
                    <small style='opacity:0.6;'>{h['time']}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

# --------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------
st.sidebar.title("🎀 StudyGenie Menu")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Profile", "Chat History"],
)

if page == "Profile":
    profile_page()
    st.stop()

if page == "Chat History":
    chat_history_page()
    st.stop()
# --------------------------------------
# PART 3 — MAIN HOME UI, CHAT + VOICE + AI (robust)
# --------------------------------------
import requests
import base64
import html
import time

# ---------- Helper: speak in browser (client-side TTS) ----------
def speak_in_browser(text, pitch=1.05, rate=0.95, volume=1.0):
    # Use JS SpeechSynthesis to speak text in the browser
    safe = html.escape(text)
    js = f"""
    <script>
    const utter = new SpeechSynthesisUtterance(`{safe}`);
    utter.pitch = {pitch};
    utter.rate = {rate};
    utter.volume = {volume};
    // prefer female voices if available
    let voices = window.speechSynthesis.getVoices();
    if (!voices.length) {{
      // try after a small delay (some browsers load voices asynchronously)
      window.speechSynthesis.onvoiceschanged = () => {{
        voices = window.speechSynthesis.getVoices();
        let found = voices.find(v => /female|korean|k-pop|korean/i.test(v.name)) || voices.find(v => v.lang.startsWith('en'));
        if(found) utter.voice = found;
        window.speechSynthesis.speak(utter);
      }};
    }} else {{
      let found = voices.find(v => /female|korean|k-pop|korean/i.test(v.name)) || voices.find(v => v.lang.startsWith('en'));
      if(found) utter.voice = found;
      window.speechSynthesis.speak(utter);
    }}
    </script>
    """
    st.components.v1.html(js, height=0)

# ---------- Voice input: prefer streamlit-webrtc if available ----------
def voice_input_ui():
    st.markdown("**Voice Input** (optional)")
    uploaded = st.file_uploader("Upload recorded audio (mp3, wav, m4a) or use mic below", type=["mp3","wav","m4a"])
    audio_text = ""
    if uploaded is not None:
        st.audio(uploaded)
        # Transcribe via OpenAI Whisper (if key present)
        key = st.secrets.get("OPENAI_API_KEY","")
        if not key:
            st.info("Add OPENAI_API_KEY in Streamlit Secrets to enable transcription.")
        else:
            try:
                # simple upload to OpenAI transcription endpoint (if allowed)
                files = {"file": (uploaded.name, uploaded.getvalue())}
                data = {"model":"gpt-4o-transcribe"}  # best-effort
                headers = {"Authorization": f"Bearer {key}"}
                resp = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=90)
                rj = resp.json()
                audio_text = rj.get("text","")
                if audio_text:
                    st.success("Transcription ready.")
                else:
                    st.warning("Transcription returned empty or failed.")
            except Exception as e:
                st.error("Transcription failed: " + str(e))
    # try to show simple mic if streamlit-webrtc is installed
    try:
        from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
        class DummyProcessor(AudioProcessorBase):
            def recv(self, frame):
                return frame
        st.write("Or use Live Mic (browser permission required)")
        webrtc_ctx = webrtc_streamer(key="mic", mode=WebRtcMode.SENDONLY, in_audio=True, audio_processor_factory=DummyProcessor)
        if webrtc_ctx and webrtc_ctx.audio_receiver:
            st.info("Live mic streaming active — press 'Record' below and upload to transcribe.")
    except Exception:
        st.info("For live mic, install `streamlit-webrtc`. For now upload audio file recorded from your phone.")

    return audio_text

# ---------- Robust AI call (retries + fallback models) ----------
def ask_ai_robust(prompt, preferred_models=None, max_retries=2, temperature=0.45, max_tokens=500):
    """
    Calls OpenAI Chat Completions REST endpoint with retries and fallback models.
    Returns text or a friendly error string starting with ❌.
    """
    key = st.secrets.get("OPENAI_API_KEY", "")
    if not key:
        return "❌ Please add OPENAI_API_KEY to Streamlit Secrets."

    if preferred_models is None:
        preferred_models = ["gpt-5-mini", "gpt-4o-mini", "gpt-4.1-mini", "gpt-3.5-turbo"]

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    system_prompt = (
        "You are StudyGenie — warm, encouraging, concise and Gen-Z friendly. "
        "Always reply in short crisp notes or 2-4 short bullet points unless user asks for longer. "
        "If asked to produce code or lists, follow a compact format. Be helpful and kind."
    )

    payload_base = {
        "messages": [
            {"role":"system", "content": system_prompt},
            {"role":"user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    for model in preferred_models:
        attempt = 0
        while attempt <= max_retries:
            attempt += 1
            payload = payload_base.copy()
            payload["model"] = model
            try:
                resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=25)
            except Exception as e:
                # network error
                if attempt > max_retries:
                    return f"❌ Network error: {e}"
                time.sleep(0.8 * attempt)
                continue

            # parse safely
            try:
                rj = resp.json()
            except Exception as e:
                if attempt > max_retries:
                    return f"❌ Invalid JSON response: {e}"
                time.sleep(0.6); continue

            # API-level error
            if "error" in rj:
                msg = rj["error"].get("message", str(rj["error"]))
                # retry on server errors/rate limit
                if attempt <= max_retries and (resp.status_code >= 500 or "rate limit" in msg.lower()):
                    time.sleep(1.0 * attempt); continue
                # otherwise return friendly error
                return f"❌ AI error: {msg}"

            choices = rj.get("choices")
            if not choices:
                if attempt <= max_retries:
                    time.sleep(0.5); continue
                # try next model
                break
            first = choices[0]
            message = first.get("message") or {}
            content = message.get("content") or message.get("text") or ""
            if not content:
                if attempt <= max_retries:
                    time.sleep(0.4); continue
                break
            return content.strip()

    # all models exhausted
    return "❌ AI did not return a valid response after multiple attempts. Try again later."

# ---------- Home page: Chat UI ----------
def home_page():
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("💬 StudyGenie Chat (Personal)")

    # theme & speak preference
    speak_pref = st.checkbox("Speak responses aloud in cute voice", value=False)
    auto_save = st.checkbox("Auto-save chats to local history", value=True)

    # show history in a vertical scroll box
    history = get_user_history(current_user)
    if history:
        # show last 50 messages
        for h in history[-200:]:
            role = h["role"]
            time_str = h["time"]
            content = h["message"]
            if role == "user":
                st.markdown(f"<div style='text-align:right; color:{current_theme['text']};'><b>You</b><br>{html.escape(content)}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:left; background:{current_theme['card']}; padding:8px; border-radius:10px; margin:6px 0;'><b style='color:{current_theme['accent']}'>Genie</b><br>{html.escape(content)}<br><small style='opacity:0.6'>{time_str}</small></div>", unsafe_allow_html=True)
    else:
        st.info("Say hi to StudyGenie! Ask any question, make notes, or use tools from the sidebar.")

    st.markdown("---")

    # input area
    user_input = st.text_area("Type your message", key="main_input", height=120)
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Send"):
            if user_input.strip():
                add_to_history(current_user, "user", user_input.strip())
                # show spinner while AI responds
                with st.spinner("StudyGenie is thinking..."):
                    ai_reply = ask_ai_robust(user_input)
                add_to_history(current_user, "assistant", ai_reply)
                if speak_pref and not ai_reply.startswith("❌"):
                    # JS TTS: slightly higher pitch for cute tone
                    speak_in_browser(ai_reply, pitch=1.08, rate=0.95, volume=0.98)
                # refresh page so new message shows
                st.experimental_rerun()
            else:
                st.warning("Write something to send.")
    with col2:
        if st.button("Upload Voice / Audio"):
            # show voice uploader and try to transcribe
            transcribed = voice_input_ui()
            if transcribed:
                st.success("Transcribed text: " + transcribed)
                st.experimental_set_query_params()  # clear any existing params
                st.session_state["main_input"] = transcribed
    with col3:
        if st.button("Clear Chat"):
            # clear this user's history
            chat_history[current_user] = []
            save_json(CHAT_DB, chat_history)
            st.success("Chat cleared.")
            st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# Run home by default unless other pages handled earlier
if page == "Home":
    home_page()
# --------------------------------------
# PART 4 — ALL TOOLS: Notes, Summary, Flashcards (SRS), Timetable, Answer Checker, Planner, Export, Theme Picker
# --------------------------------------
import io
import zipfile

# ---------- THEME PICKER (live) ----------
def theme_picker_ui():
    st.sidebar.subheader("🎨 Theme")
    theme_choice = st.sidebar.selectbox("Choose theme", list(THEMES.keys()), index=list(THEMES.keys()).index(current_profile.get("theme", "Pastel Sky")))
    if st.sidebar.button("Apply Theme"):
        profiles[current_user]["theme"] = theme_choice
        save_json(PROFILE_DB, profiles)
        # update runtime current_theme var
        global current_theme
        current_theme = THEMES.get(theme_choice)
        st.experimental_rerun()

# call once to show on sidebar
theme_picker_ui()

# ---------- NOTES GENERATOR ----------
def notes_generator_ui():
    st.subheader("📝 Notes Generator")
    topic = st.text_input("Topic for notes", key="notes_topic")
    length = st.selectbox("Length", ["Short (3-5 bullets)", "Medium (6-9 bullets)", "Long (10+ bullets)"])
    if st.button("Generate Notes"):
        if not topic.strip():
            st.warning("Please enter a topic.")
            return
        prompt = f"Create {length.lower()} for the topic: {topic}. Keep bullet points short and crisp, suitable for quick revision."
        with st.spinner("Creating notes..."):
            out = ask_ai_robust(prompt)
        st.markdown(f"<div style='padding:12px; border-radius:10px; background:{current_theme['card']};'>{out}</div>", unsafe_allow_html=True)
        if st.button("Save Notes"):
            notes_store = profiles[current_user].setdefault("notes", [])
            notes_store.append({"title": topic, "content": out, "time": str(datetime.now())})
            save_json(PROFILE_DB, profiles)
            st.success("Notes saved to your profile.")

# ---------- SUMMARY / BRAIN-DUMP CLEANER ----------
def summary_ui():
    st.subheader("🧾 Summary Maker / Brain-Dump Cleaner")
    text = st.text_area("Paste text or messy notes here", height=200, key="summary_input")
    style = st.selectbox("Style", ["Bulleted short summary", "Very short 3-line summary", "Organized titled sections with action items"])
    if st.button("Process"):
        if not text.strip():
            st.warning("Paste or write something first.")
            return
        prompt = f"{style}. Content:\n{text}\nKeep it concise and easy to revise."
        with st.spinner("Processing..."):
            out = ask_ai_robust(prompt)
        st.markdown(f"<div style='padding:12px; border-radius:10px; background:{current_theme['card']};'>{out}</div>", unsafe_allow_html=True)
        if st.button("Save Summary"):
            summaries = profiles[current_user].setdefault("summaries", [])
            summaries.append({"title": "Summary " + datetime.now().strftime("%Y-%m-%d %H:%M"), "content": out})
            save_json(PROFILE_DB, profiles)
            st.success("Saved to your profile.")

# ---------- TIMETABLE BUILDER ----------
def timetable_ui():
    st.subheader("📅 Timetable Builder")
    subjects = st.text_input("Subjects (comma separated)", key="tt_subjects")
    hours = st.slider("Total study hours per day", 1, 12, 5, key="tt_hours")
    if st.button("Build Timetable"):
        if not subjects.strip():
            st.warning("Add subjects first.")
            return
        subs = [s.strip() for s in subjects.split(",") if s.strip()]
        per = round(hours / len(subs), 2)
        timetable = "\n".join([f"• {s}: {per} hours" for s in subs])
        st.markdown(f"<div style='padding:12px; border-radius:10px; background:{current_theme['card']};'>{timetable}</div>", unsafe_allow_html=True)
        if st.button("Save Timetable"):
            plans = profiles[current_user].setdefault("timetables", [])
            plans.append({"title": "Timetable " + datetime.now().strftime("%Y-%m-%d"), "content": timetable})
            save_json(PROFILE_DB, profiles)
            st.success("Timetable saved.")

# ---------- FLASHCARDS (simple generator + review with SRS-like spacing) ----------
def flashcards_ui():
    st.subheader("🃏 Flashcards (generate & review)")
    topic = st.text_input("Flashcard topic", key="fc_topic")
    count = st.slider("Number of cards", 3, 20, 6, key="fc_count")
    if st.button("Generate Flashcards"):
        if not topic.strip():
            st.warning("Enter a topic.")
            return
        prompt = f"Create {count} concise Q/A flashcards for: {topic}. Format as Q: ... A: ..."
        with st.spinner("Generating cards..."):
            out = ask_ai_robust(prompt)
        # parse Q/A
        cards = []
        qtmp = None
        for line in out.splitlines():
            line = line.strip()
            if line.lower().startswith("q:"):
                qtmp = line.split(":",1)[1].strip()
            elif line.lower().startswith("a:") and qtmp:
                a = line.split(":",1)[1].strip()
                cards.append({"q": qtmp, "a": a, "interval": 1, "ease": 2.5, "reviews": 0})
                qtmp = None
        if not cards:
            # fallback: split by double newline
            parts = [p.strip() for p in out.split("\n\n") if p.strip()]
            for p in parts:
                if ":" in p:
                    k,v = p.split(":",1)
                    cards.append({"q": k.strip()[:200], "a": v.strip(), "interval":1, "ease":2.5, "reviews":0})
        # save to profile
        profiles[current_user].setdefault("flashcards", []).extend(cards)
        save_json(PROFILE_DB, profiles)
        st.success(f"Saved {len(cards)} cards to your profile.")

    # review mode
    fc_list = profiles[current_user].get("flashcards", [])
    if fc_list:
        st.markdown("**Review Mode**")
        idx = st.session_state.get("fc_idx", 0)
        if idx >= len(fc_list): idx = 0
        card = fc_list[idx]
        st.markdown(f"**Q:** {card['q']}")
        if st.button("Show Answer"):
            st.markdown(f"**A:** {card['a']}")
            col_e = st.columns(3)
            if col_e[0].button("Easy"):
                card["reviews"] += 1
                card["interval"] = int(card.get("interval",1) * 2)
                card["ease"] = min(3.5, card.get("ease",2.5) + 0.2)
                st.success("Marked Easy.")
            if col_e[1].button("Good"):
                card["reviews"] += 1
                card["interval"] = int(card.get("interval",1) * 1.5) or 1
                st.success("Marked Good.")
            if col_e[2].button("Hard"):
                card["reviews"] += 1
                card["interval"] = max(1, int(card.get("interval",1) * 0.7))
                card["ease"] = max(1.3, card.get("ease",2.5) - 0.2)
                st.success("Marked Hard.")
            # persist progress and advance index
            profiles[current_user]["flashcards"] = fc_list
            save_json(PROFILE_DB, profiles)
            st.session_state["fc_idx"] = (idx + 1) % len(fc_list)
            st.experimental_rerun()
    else:
        st.info("No flashcards yet. Generate some!")

# ---------- ANSWER CHECKER ----------
def answer_checker_ui():
    st.subheader("✅ Answer Checker")
    question = st.text_input("Question")
    student_ans = st.text_area("Student's answer")
    if st.button("Check Answer"):
        if not question.strip() or not student_ans.strip():
            st.warning("Fill both fields.")
            return
        prompt = f"Grade this answer out of 10 and provide short feedback and corrections. Question: {question}\nStudent answer: {student_ans}"
        with st.spinner("Checking..."):
            out = ask_ai_robust(prompt)
        st.markdown(f"<div style='padding:12px; border-radius:10px; background:{current_theme['card']};'>{out}</div>", unsafe_allow_html=True)
        add_to_history(current_user, "assistant", "Checked an answer. " + (out if len(out) < 300 else out[:300]+"..."))

# ---------- PLANNER (tasks + 7-day plan) ----------
def planner_ui():
    st.subheader("🗓 Planner")
    new_task = st.text_input("New Task")
    new_when = st.text_input("When (optional)")
    if st.button("Add Task"):
        if not new_task.strip():
            st.warning("Enter a task.")
            return
        tasks = profiles[current_user].setdefault("tasks", [])
        tasks.append({"task": new_task, "when": new_when, "added": str(datetime.now())})
        save_json(PROFILE_DB, profiles)
        st.success("Task added.")
    # show tasks
    tasks = profiles[current_user].get("tasks", [])
    if tasks:
        for i,t in enumerate(tasks,1):
            st.write(f"{i}. {t['task']} — {t.get('when','')} (Added: {t.get('added')})")
        if st.button("Generate 7-day study plan from tasks"):
            prompt = "Create a 7-day study plan from these tasks:\n" + "\n".join([p["task"] for p in tasks])
            with st.spinner("Creating plan..."):
                out = ask_ai_robust(prompt)
            st.markdown(f"<div style='padding:12px; border-radius:10px; background:{current_theme['card']};'>{out}</div>", unsafe_allow_html=True)
            profiles[current_user].setdefault("plans", []).append({"title":"7-day plan "+datetime.now().strftime("%Y-%m-%d"), "content": out})
            save_json(PROFILE_DB, profiles)
            st.success("Plan saved to profile.")

# ---------- EXPORT / DOWNLOAD saved chats & notes ----------
def export_ui():
    st.subheader("💾 Export / Download")

    if st.button("Download my chats (ZIP)"):
        # prepare in-memory zip
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
            # add chat history
            user_hist = get_user_history(current_user)
            z.writestr(f"{current_user}_chats.json", json.dumps(user_hist, indent=2))
            # add profile data
            z.writestr(f"{current_user}_profile.json", json.dumps(profiles.get(current_user, {}), indent=2))
        mem.seek(0)
        st.download_button("Download ZIP", mem, file_name=f"{current_user}_studygenie_data.zip")

# ---------- TOOLS ROUTER (integrate in main app page) ----------
def tools_router():
    st.sidebar.subheader("Tools")
    tool_choice = st.sidebar.selectbox("Pick a tool", ["Notes Generator", "Summary Maker", "Timetable", "Flashcards", "Answer Checker", "Planner", "Export Data"])
    if tool_choice == "Notes Generator":
        notes_generator_ui()
    elif tool_choice == "Summary Maker":
        summary_ui()
    elif tool_choice == "Timetable":
        timetable_ui()
    elif tool_choice == "Flashcards":
        flashcards_ui()
    elif tool_choice == "Answer Checker":
        answer_checker_ui()
    elif tool_choice == "Planner":
        planner_ui()
    elif tool_choice == "Export Data":
        export_ui()

# call router inside Home (so it shows in sidebar and main)
if page == "Home":
    tools_router()
# --------------------------
# PART 5 — MOTIVATION BOOSTERS (55 items, 2–3 lines each)
# --------------------------
import random

MOTIVATIONS = [
"""You are becoming stronger and more skilled every day. Small actions now create large results later.""",

"""Your consistency is quietly building a remarkable future. Trust the process and keep showing up.""",

"""Every hour of focused work is a gift to your future self. You are planting seeds that will bloom.""",

"""You deserve calm confidence and peaceful success. Your effort is shaping a life you will be proud of.""",

"""You are learning and improving even when progress feels slow. Growth is happening, and it is real.""",

"""Your discipline today becomes your freedom tomorrow. Keep building the habits that serve you.""",

"""You are not defined by one moment or one result. Your journey is long and full of beautiful beginnings.""",

"""Every small win adds up to a meaningful life. Celebrate the tiny victories and keep moving forward.""",

"""You are becoming someone who solves problems with grace. Your mind is getting sharper and more confident.""",

"""The future you are creating is soft, abundant, and steady. Continue to take kind, purposeful steps.""",

"""You are allowed to rest and continue at your own pace. Balance is a part of long term success.""",

"""Each chapter you complete teaches you something new. Your knowledge is stacking in the best possible way.""",

"""You are developing focus and clarity each week. Those qualities will open doors you have not seen yet.""",

"""Your persistence will outlast every short lived challenge. Keep steady and trust your path.""",

"""You are crafting a life that feels intentional and beautiful. Your effort is not wasted.""",

"""You are becoming someone who inspires even by simple actions. Your small routines make a big difference.""",

"""You are learning to manage your energy and protect your time. That skill is more valuable than you think.""",

"""Your dedication is shaping opportunities that will feel effortless later. Keep investing in yourself.""",

"""You are learning the art of consistent improvement. That is the real secret of lasting success.""",

"""Your future self is thankful for the choices you are making today. Continue to invest in your growth.""",

"""You are stronger than the doubts that appear in your mind. Your actions prove your capability.""",

"""Every page you study adds depth to your thinking. Your knowledge will become your advantage.""",

"""You are building routines that become your identity. Small habits make big outcomes over time.""",

"""You are allowed to be imperfect and still progress. Perfection is unnecessary, progress is essential.""",

"""Your vision is clearer because you keep working at it. Clarity grows from steady attention.""",

"""You are learning to trust your own rhythm. There is power in moving at your natural pace.""",

"""You are becoming resilient in a kind and steady way. Challenges are shaping constructive strength.""",

"""Your curiosity is a compass guiding you to better knowledge. Keep asking, exploring, and practicing.""",

"""You are designing a future that aligns with your values. That alignment makes success sweeter and calmer.""",

"""You are learning how to turn effort into results. Skill is built by repetition and thoughtful practice.""",

"""You are allowed to change direction and still win. Flexibility is part of a smart strategy.""",

"""Your consistency is like a quiet engine moving everything forward. Trust it even when you cannot see immediate reward.""",

"""You are slowly constructing a life you admiration. Small choices made daily produce meaningful change.""",

"""You are becoming someone who completes their promises to themselves. That trust is the foundation of growth.""",

"""You are building a life with intention and care. That life will feel stable, joyful, and meaningful.""",

"""You are learning how to stay focused under pressure. That ability will serve you for years to come.""",

"""You are creating a future that honors your effort. Every hour counts and every effort matters.""",

"""You are moving toward opportunities that match your work ethic. The world rewards steady, persistent effort.""",

"""You are allowed to be patient while you build something great. Patience compounds with consistent practice.""",

"""You are becoming more capable than you imagine. Keep practicing the fundamentals and trust the progress.""",

"""You are developing patterns that support your ambitions. Habit is the architecture of success.""",

"""You are allowed to rest without guilt and return refreshed. Rest is part of sustainable growth.""",

"""You are learning to set boundaries that protect your focus. That discipline is an act of self love.""",

"""You are steadily improving in ways that become obvious over time. Keep going; the change is real.""",

"""You are a builder of your future life, one small choice at a time. That reality is powerful and true.""",

"""You are cultivating calm confidence every day. Confidence grows from repeated, successful effort.""",

"""You are turning your goals into daily practices. That is how dreams become reliable realities.""",

"""You are learning to make consistent progress, not dramatic leaps. Small progress is still powerful progress.""",

"""You are growing a skill set that will support your independence. Your work is building long term freedom.""",

"""You are prepared for good things by how you spend your time now. Your future will reflect your current choices.""",

"""You are becoming disciplined and kind to yourself. Both qualities together create meaningful success.""",

"""You are learning the graceful art of finishing tasks. Completion is a skill that brings confidence and momentum.""",

"""You are building momentum through repeated small wins. Momentum makes difficult days easier.""",

"""You are capable of more than you currently believe. Keep challenging yourself with kind persistence.""",

"""You are cultivating the habits that successful people share. Consistency and clarity are your allies.""",

"""You are allowed to adjust your path while keeping the goal. Course correction is a smart strategy, not failure.""",

"""You are designing a future that feels peaceful and capable. Keep practicing; your future self is rooting for you.""",
]

def random_motivation():
    return random.choice(MOTIVATIONS)
# --------------------------
# PART 6 — MAIN APP UI + FIXED AI RESPONSE SYSTEM
# --------------------------

import streamlit as st
import json
import os

# ---- UI STYLING ----
st.markdown("""
<style>

body {
    background: linear-gradient(135deg, #f8d3ff 0%, #cde6ff 50%, #ffd6e8 100%);
    font-family: 'Poppins', sans-serif;
}

.big-title {
    font-size: 42px;
    font-weight: 700;
    color: #4a4a4a;
    text-align: center;
    margin-bottom: 20px;
}

.section-title {
    font-size: 26px;
    font-weight: 600;
    margin-top: 25px;
    color: #444;
}

.motivation-box {
    padding: 18px;
    background: rgba(255,255,255,0.65);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.4);
    backdrop-filter: blur(6px);
    animation: popIn 0.45s ease;
    font-size: 18px;
    line-height: 1.5;
    font-weight: 500;
}

@keyframes popIn {
    0% { transform: scale(0.9); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

.answer-box {
    padding: 15px;
    background: rgba(255,255,255,0.55);
    border-radius: 15px;
    font-size: 16px;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='big-title'>✨ StudyGenie — Your Cute AI Bestie ✨</h1>", unsafe_allow_html=True)

# ---- LOCAL CHAT HISTORY (NO FIREBASE) ----
if "history" not in st.session_state:
    st.session_state.history = []

if "saved_boosters" not in st.session_state:
    st.session_state.saved_boosters = []

# ---- FIXED OPENAI CALL (NO MORE INVALID ERRORS) ----
def call_ai(prompt):
    try:
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=180,
            temperature=0.4,
        )
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return f"AI could not respond right now 💔 Error: {str(e)}"


# -------------------------
# DOUBT SOLVER SECTION
# -------------------------
st.markdown("<div class='section-title'>🔮 Doubt Solver</div>", unsafe_allow_html=True)
question = st.text_input("Ask your doubt bestie:")

if st.button("Solve ✨"):
    if question.strip() != "":
        answer = call_ai(
            f"Give a short & crispy note-style explanation for this doubt:\n{question}"
        )
        st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)
        st.session_state.history.append({"q": question, "a": answer})


# -------------------------
# MOTIVATION BOOSTER SECTION
# -------------------------
st.markdown("<div class='section-title'>💞 Motivation Booster</div>", unsafe_allow_html=True)

if "current_boost" not in st.session_state:
    st.session_state.current_boost = random_motivation()

if st.button("New Motivation 🌟"):
    st.session_state.current_boost = random_motivation()

st.markdown(f"<div class='motivation-box'>{st.session_state.current_boost}</div>", unsafe_allow_html=True)

if st.button("Save This Booster 💗"):
    st.session_state.saved_boosters.append(st.session_state.current_boost)


# -------------------------
# SAVED BOOSTERS PAGE
# -------------------------
if st.checkbox("Show Saved Boosters 💌"):
    for i, b in enumerate(st.session_state.saved_boosters):
        st.write(f"✨ {b}")
        st.write("---")
# ------------------------------
# PART 7 — LOGIN, THEMES, PROFILE, VOICE
# ------------------------------

import streamlit as st
from streamlit.components.v1 import html
import base64
import requests

# ------------------------------
# SESSION INIT
# ------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = "Guest"

if "theme" not in st.session_state:
    st.session_state.theme = "Baby Pink"

if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "",
        "age": "",
        "goal": "",
        "vibe": "Cute + Study + Glow 💖"
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# ------------------------------
# THEME SYSTEM
# ------------------------------
THEMES = {
    "Baby Pink": "linear-gradient(135deg, #ffd6e8, #ffe3f1, #ffc9df)",
    "Sky Blue": "linear-gradient(135deg, #cde6ff, #b9dcff, #d7f0ff)",
    "Lavender Dream": "linear-gradient(135deg, #e7d4ff, #d2b9ff, #f0e6ff)",
    "K-Idol Dark": "linear-gradient(135deg, #1a1a1a, #2b2b2b, #1f1f1f)"
}

def apply_theme():
    bg = THEMES[st.session_state.theme]
    css = f"""
    <style>
    body {{
        background: {bg} !important;
        font-family: 'Poppins', sans-serif;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

apply_theme()

# ------------------------------
# LOGIN PAGE
# ------------------------------
def login_page():
    st.markdown("<h1 style='text-align:center;'>✨ StudyGenie Login ✨</h1>", unsafe_allow_html=True)
    
    name = st.text_input("Enter your name bestie:")
    
    if st.button("Login 💗"):
        if name.strip():
            st.session_state.username = name
            st.session_state.logged_in = True
            
            if name not in st.session_state.chat_history:
                st.session_state.chat_history[name] = []
            
            st.experimental_rerun()

    st.markdown("<p style='text-align:center;'>Or continue as <b>Guest</b>.</p>", unsafe_allow_html=True)
    if st.button("Use as Guest 🚀"):
        st.session_state.logged_in = True
        st.experimental_rerun()

# ------------------------------
# PROFILE PAGE
# ------------------------------
def profile_page():
    st.markdown("<h2>💫 Your Profile</h2>", unsafe_allow_html=True)

    st.session_state.profile["name"] = st.text_input("Your Name:", st.session_state.profile["name"])
    st.session_state.profile["age"] = st.text_input("Your Age:", st.session_state.profile["age"])
    st.session_state.profile["goal"] = st.text_input("Your Main Goal:", st.session_state.profile["goal"])
    st.session_state.profile["vibe"] = st.text_input("Your Vibe:", st.session_state.profile["vibe"])

    if st.button("Save Profile 💕"):
        st.success("Profile updated bestie 💖")

# ------------------------------
# CHAT HISTORY PAGE
# ------------------------------
def history_page():
    st.markdown(f"<h2>📚 Chat History — {st.session_state.username}</h2>", unsafe_allow_html=True)

    user = st.session_state.username
    if user in st.session_state.chat_history:
        for msg in st.session_state.chat_history[user]:
            st.write(f"💬 **You:** {msg['q']}")
            st.write(f"✨ **Genie:** {msg['a']}")
            st.write("---")
    else:
        st.info("No chats yet bestie 😭")

# ------------------------------
# VOICE INPUT (Android Friendly)
# ------------------------------
def voice_input():
    st.markdown("🎤 **Voice Input**")
    audio = st.audio_input("Speak your doubt bestie:")
    if audio:
        try:
            result = base64.b64encode(audio.getvalue()).decode("utf-8")
            return "[Voice Input Detected]"
        except:
            return None

# ------------------------------
# TEXT-TO-SPEECH (K-pop style)
# ------------------------------
def cute_voice(text):
    try:
        tts = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini-tts",
                "voice": "alloy",
                "input": text
            }
        )
        audio_data = tts.content
        st.audio(audio_data, format="audio/mp3")
    except:
        st.warning("Voice reply failed 😭")

# ------------------------------
# SIDEBAR MENU
# ------------------------------
if st.session_state.logged_in:
    choice = st.sidebar.radio(
        "Menu",
        ["Home", "Profile", "Themes", "Chat History"]
    )

    if choice == "Profile":
        profile_page()

    if choice == "Themes":
        st.markdown("<h2>🎨 Choose a Theme</h2>", unsafe_allow_html=True)
        st.session_state.theme = st.selectbox("Pick Aesthetic:", list(THEMES.keys()))
        apply_theme()

    if choice == "Chat History":
        history_page()

else:
    login_page()


# -------------------------
# CHAT HISTORY SECTION
# -------------------------
if st.checkbox("Show Chat History 📚"):
    for item in st.session_state.history:
        st.write(f"💭 **You:** {item['q']}")
        st.write(f"✨ **Genie:** {item['a']}")
        st.write("---")