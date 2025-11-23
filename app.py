# app.py — StudyGenie Ultra (All-in-one Streamlit)
# Paste this entire file into your Streamlit app folder as app.py

import streamlit as st
import requests, json, os, time, io, zipfile, html, base64, random
from datetime import datetime

# -----------------------------
# CONFIG + FILE PATHS
# -----------------------------
st.set_page_config(page_title="StudyGenie Ultra", layout="wide")
USER_DB = "users.json"
PROFILE_DB = "profiles.json"
CHAT_DB = "chat_history.json"

# -----------------------------
# HELPERS: JSON load/save
# -----------------------------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_json(USER_DB, {})
profiles = load_json(PROFILE_DB, {})
chat_history = load_json(CHAT_DB, {})  # structure: {username: {tool_name: [ {role,msg,time} ] } }

# -----------------------------
# THEMES
# -----------------------------
THEMES = {
    "Pastel Sky": {"bg": "linear-gradient(170deg,#dff3ff,#f5dfff,#ffe6f2)","card":"#ffffffaa","accent":"#A7C7E7","text":"#1A1A1A"},
    "Baby Pink": {"bg": "linear-gradient(170deg,#ffeaf4,#fff0f6,#ffdff0)","card":"#ffffffaa","accent":"#FFB7D5","text":"#1A1A1A"},
    "Lavender Dream": {"bg":"linear-gradient(170deg,#f1e7ff,#efe0ff,#fff0fb)","card":"#ffffffaa","accent":"#D6B8FF","text":"#1A1A1A"},
    "K-Idol Dark": {"bg":"linear-gradient(170deg,#0d0d0d,#1a1a1a,#111111)","card":"#1a1a1aaa","accent":"#7A5FFF","text":"#ffffff"},
}

# -----------------------------
# AESTHETIC CSS (Base + Dynamic Theme)
# -----------------------------

def apply_theme_css(theme_name):
    theme_data = THEMES.get(theme_name, THEMES["Pastel Sky"])
    bg_color = theme_data["bg"]
    card_color = theme_data["card"]
    accent_color = theme_data["accent"]
    text_color = theme_data["text"]

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ 
        font-family: 'Poppins', sans-serif; 
        background: {bg_color}; /* Apply dynamic background */
        color: {text_color};
    }}
    .header {{ text-align:center; }}
    .section {{ background: {card_color}; padding:18px; border-radius:14px; margin:12px 0; backdrop-filter: blur(6px); color: {text_color};}}
    .genie {{ background: rgba(255,255,255,0.8); padding:12px; border-radius:12px; margin:10px 0; color: #1A1A1A; }}
    .user {{ background: {accent_color}e0; padding:10px; border-radius:12px; margin:8px 0; text-align:right; color: #1A1A1A; }}
    .small {{ font-size:13px; opacity:0.7; }}
    [data-testid="stSidebar"] {{ background: {card_color}; }}
    h1, h2, h3, h4, h5, h6 {{ color: {text_color}; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------
# SESSION STATE init
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = "Guest"
if "current_tool" not in st.session_state:
    st.session_state.current_tool = "AI Doubt Solver"
if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "Pastel Sky"
if "chat_session" not in st.session_state:
    # chat_session stores messages for current tool in-memory while user is active
    st.session_state.chat_session = []

# Apply the initial or saved theme
apply_theme_css(st.session_state.ui_theme)


# -----------------------------
# MOTIVATIONS (55 multi-line)
# -----------------------------
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
]

def random_motivation():
    return random.choice(MOTIVATIONS)

# -----------------------------
# UTILS: per-user & per-tool history
# -----------------------------
def get_user_tool_history(username, tool):
    user_hist = chat_history.get(username, {})
    return user_hist.get(tool, [])

def add_user_tool_history(username, tool, role, message):
    if username not in chat_history:
        chat_history[username] = {}
    if tool not in chat_history[username]:
        chat_history[username][tool] = []
    chat_history[username][tool].append({"role": role, "message": message, "time": str(datetime.now())})
    save_json(CHAT_DB, chat_history)

# -----------------------------
# ROBUST OPENAI CALL (fallbacks + retries)
# -----------------------------
def ask_ai_robust(prompt, preferred_models=None, max_retries=2, temperature=0.45, max_tokens=350):
    key = st.secrets.get("OPENAI_API_KEY", "")
    if not key:
        return "❌ Please add OPENAI_API_KEY to Streamlit Secrets."

    if preferred_models is None:
        preferred_models = ["gpt-4o-mini", "gpt-3.5-turbo"] # Corrected preferred model list

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    system_prompt = ("You are StudyGenie — warm, encouraging, concise and Gen-Z friendly. "
                     "Always reply in short crisp notes (2–4 bullets) unless user asks for long.")
    payload_base = {"messages": [{"role":"system","content":system_prompt}, {"role":"user","content":prompt}],
                    "temperature": temperature, "max_tokens": max_tokens}

    for model in preferred_models:
        attempt = 0
        while attempt <= max_retries:
            attempt += 1
            payload = dict(payload_base)
            payload["model"] = model
            try:
                resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            except Exception as e:
                if attempt > max_retries:
                    return f"❌ Network error: {e}"
                time.sleep(0.8 * attempt)
                continue

            try:
                rj = resp.json()
            except Exception as e:
                if attempt > max_retries:
                    return f"❌ Invalid JSON: {e}"
                time.sleep(0.5)
                continue

            if "error" in rj:
                err = rj["error"].get("message", str(rj["error"]))
                # retry on server/rate-limit
                if attempt <= max_retries and (resp.status_code >= 500 or "rate limit" in err.lower()):
                    time.sleep(1.0 * attempt)
                    continue
                return f"❌ AI error: {err}"

            choices = rj.get("choices")
            if not choices:
                if attempt <= max_retries:
                    time.sleep(0.5)
                    continue
                break
            msg = choices[0].get("message") or {}
            content = msg.get("content") or msg.get("text") or ""
            if not content:
                if attempt <= max_retries:
                    time.sleep(0.4)
                    continue
                break
            return content.strip()

    return "❌ AI did not return a valid response after multiple attempts. Try again later."

# -----------------------------
# BROWSER TTS (client-side) — cute tone
# -----------------------------
def speak_in_browser(text, pitch=1.05, rate=0.95, volume=0.98):
    safe = html.escape(text)
    js = f"""
    <script>
    const u = new SpeechSynthesisUtterance(`{safe}`);
    u.pitch = {pitch}; u.rate = {rate}; u.volume = {volume};
    const voices = window.speechSynthesis.getVoices();
    let found = voices.find(v => /female|korean|noto/i.test(v.name)) || voices.find(v => v.lang.startsWith('en')) || voices[0];
    if(found) u.voice = found;
    window.speechSynthesis.speak(u);
    </script>
    """
    st.components.v1.html(js, height=0)

# -----------------------------
# VOICE TRANSCRIPTION via upload (Whisper endpoints if available)
# -----------------------------
def transcribe_audio_file(uploaded):
    key = st.secrets.get("OPENAI_API_KEY", "")
    if not key:
        return ""
    try:
        # Use the correct Whisper API endpoint and model
        files = {"file": (uploaded.name, uploaded.getvalue())}
        data = {"model": "whisper-1"}
        headers = {"Authorization": f"Bearer {key}"}
        resp = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=90)
        rj = resp.json()
        return rj.get("text", "")
    except Exception:
        return ""

# -----------------------------
# PROMPT ROUTING (ADDED: This was missing/corrupted)
# -----------------------------
def route_prompt_for_tool(tool, user_text):
    """Adds a system-level instruction based on the tool for better AI response."""
    
    # Tool-specific instructions for the AI
    instructions = {
        "AI Doubt Solver": "Answer the question directly, providing a clear explanation and one simple example.",
        "Notes Generator": "Convert the user's topic into concise, structured study notes with headings and bullet points.",
        "Summary Maker": "Provide a 3-sentence summary and 3 key takeaways (bullet points) for the given text/topic.",
        "Timetable Builder": "Create a study timetable or schedule based on the user's input. Use a clear, formatted list or table.",
        "Motivation Booster": f"Deliver a powerful, positive, and Gen-Z-friendly motivational message. Also include this quote: '{random_motivation()}'",
        "Flashcards": "Create 3-5 Question/Answer flashcards based on the user's topic or text. Format clearly with Q: and A:.",
        "Brain-Dump Cleaner": "Take the user's scattered thoughts and organize them into 3-4 logical, actionable steps or categories.",
        "Answer Checker": "Analyze the user's answer to a question. Give a score out of 10 and 2 clear points of improvement.",
        "AI Planner": "Help the user break down a long-term goal (e.g., 'pass my exam') into a 3-step action plan for this week.",
        "Mindset Reset": "Provide a simple 2-minute relaxation or focus technique and a short affirmation.",
        "Study Routine Designer": "Design a simple, 3-hour focused study block based on the user's preferred time of day.",
        "Exam Strategy Maker": "Give 3 tactical tips for the user to approach their next exam (e.g., time management, question selection).",
        "Personal Study Coach": "Provide supportive, personalized feedback or advice on the user's study habits or problem.",
    }
    
    instruction = instructions.get(tool, "Act as a helpful study guide and answer the question concisely.")
    
    # Combine the tool instruction with the user's input
    full_prompt = f"TOOL INSTRUCTION: {instruction}\nUSER INPUT: {user_text}"
    return full_prompt


# -----------------------------
# THE UI: Header + Sidebar login + theme
# -----------------------------
st.markdown("<div class='header'><h1>✨ StudyGenie Ultra — Your AI Study Bestie 💕</h1></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#5f569b;'>Ask questions, take notes, build timetables, and glow up ✨</p>", unsafe_allow_html=True)

# Sidebar: login / profile / theme / export
st.sidebar.title("StudyGenie Menu")
if not st.session_state.logged_in:
    st.sidebar.subheader("Login")
    name = st.sidebar.text_input("Enter a display name", value="")
    if st.sidebar.button("Login / Continue"):
        if name.strip():
            # Basic validation to prevent key errors or overwrite
            clean_name = name.strip()
            if clean_name not in users:
                users[clean_name] = {"created": str(datetime.now())}
                profiles[clean_name] = {"theme":"Pastel Sky", "avatar_color":"#FFB7D5"}
                save_json(USER_DB, users); save_json(PROFILE_DB, profiles)
            st.session_state.logged_in = True
            st.session_state.username = clean_name
            # Set the theme based on profile data
            prof_theme = profiles.get(clean_name, {}).get("theme", "Pastel Sky")
            st.session_state.ui_theme = prof_theme
            # Rerun to apply new theme immediately
            st.success(f"Welcome, {clean_name}!")
            st.experimental_rerun()
else:
    st.sidebar.markdown(f"**Signed in as:** {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = "Guest"
        st.session_state.chat_session = []
        st.experimental_rerun()

# Theme picker
theme_choice = st.sidebar.selectbox("Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.ui_theme))
if theme_choice != st.session_state.ui_theme:
    st.session_state.ui_theme = theme_choice
    # Update profile with new theme
    if st.session_state.logged_in:
        profiles[st.session_state.username]["theme"] = theme_choice
        save_json(PROFILE_DB, profiles)
    st.experimental_rerun()


# small profile quick edit
st.sidebar.subheader("Profile")
if st.session_state.logged_in:
    prof = profiles.get(st.session_state.username, {})
    # Use prof.get('display_name', st.session_state.username) for current value
    name_val = st.sidebar.text_input("Display name", value=prof.get('display_name', st.session_state.username)) 
    avatar = st.sidebar.color_picker("Avatar color", value=prof.get("avatar_color","#FFB7D5"))
    if st.sidebar.button("Save Profile"):
        # The user's actual username (key in the DB) should not change here easily, only display details
        profiles[st.session_state.username]["avatar_color"] = avatar
        profiles[st.session_state.username]["display_name"] = name_val
        profiles[st.session_state.username]["theme"] = st.session_state.ui_theme # Ensure theme is also saved
        save_json(PROFILE_DB, profiles)
        st.success("Profile saved!")

# Export / download
st.sidebar.markdown("---")
if st.sidebar.button("Export My Data (ZIP)"):
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        user_profile_data = profiles.get(st.session_state.username, {})
        user_chat_data = chat_history.get(st.session_state.username, {})
        
        # Write data to the zip file
        z.writestr(f"{st.session_state.username}_profile.json", json.dumps(user_profile_data, indent=2))
        z.writestr(f"{st.session_state.username}_chats.json", json.dumps(user_chat_data, indent=2))
    
    mem.seek(0)
    st.sidebar.download_button("Download ZIP", data=mem, file_name=f"{st.session_state.username}_studygenie.zip")

# -----------------------------
# TOOL SELECTION
# -----------------------------
tool = st.sidebar.radio("Choose tool", [
    "AI Doubt Solver","Notes Generator","Summary Maker","Timetable Builder","Motivation Booster",
    "Flashcards","Brain-Dump Cleaner","Answer Checker","AI Planner","Mindset Reset",
    "Study Routine Designer","Exam Strategy Maker","Personal Study Coach"
])
st.session_state.current_tool = tool

# Sidebar: show per-tool recent history (last 10 messages)
st.sidebar.markdown("### Recent (this tool)")
recent = get_user_tool_history(st.session_state.username, tool)[-12:]
if not recent:
    st.sidebar.write("No recent chat for this tool.")
else:
    # Reverse the order so the most recent messages are at the top of the sidebar list
    for entry in reversed(recent):
        who = entry["role"]
        msg = entry["message"]
        tm = entry["time"].split(".")[0] # Clean up time for display
        # Use an appropriate background color for the sidebar
        bg_style = 'background:rgba(255,255,255,0.6);' if who == 'assistant' else 'background:rgba(170,200,255,0.6);'
        st.sidebar.markdown(f"<div style='padding:6px;border-radius:8px;{bg_style}'><b class='small'>{who}</b>: {html.escape(msg)[:60]}...<br><small class='small'>{tm}</small></div>", unsafe_allow_html=True)


# -----------------------------
# TOOL: helper to render chat UI for this tool (FIXED AND COMPLETED)
# -----------------------------
def tool_chat_ui():
    current_tool = st.session_state.current_tool
    
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader(f"🔹 {current_tool}")
    
    # Load previous messages for this tool
    hist = get_user_tool_history(st.session_state.username, current_tool)
    
    # Use a container to scroll the chat history
    chat_container = st.container()
    
    # Display chat history within the container
    with chat_container:
        if hist:
            for m in hist[-200:]: # Limit to 200 messages for performance
                if m["role"] == "user":
                    st.markdown(f"<div class='user'>{html.escape(m['message'])}<br><small class='small'>{m['time'].split('.')[0]}</small></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='genie'><b>Genie</b><br>{m['message']}<br><small class='small'>{m['time'].split('.')[0]}</small></div>", unsafe_allow_html=True)
            # Scroll to the bottom of the history after rendering
            st.markdown('<script>window.scrollTo(0, document.body.scrollHeight);</script>', unsafe_allow_html=True)
        else:
            st.info(f"No messages yet for **{current_tool}**. Ask anything related to this tool!")

    st.markdown("---")
    
    # Input area and voice upload
    col1, col2 = st.columns([4,1])
    
    # Initialize the input key's value in session_state if it doesn't exist
    input_key = f"input_{current_tool}"
    if input_key not in st.session_state:
        st.session_state[input_key] = ""

    with col1:
        # Use the stored session state value for the text area
        user_text = st.text_area("Type your message", key=input_key, height=120, value=st.session_state[input_key])
        # Update session state with the text area content on every change
        st.session_state[input_key] = user_text 
        
    with col2:
        uploaded = st.file_uploader("Upload audio (mp3/wav/m4a)", type=["mp3","wav","m4a"], key=f"up_{current_tool}")
        if uploaded:
            st.audio(uploaded)
            # Ensure transcription only runs once per upload
            if f"transcription_{current_tool}" not in st.session_state or st.session_state[f"transcription_file_{current_tool}"] != uploaded.name:
                with st.spinner("Transcribing audio..."):
                    trans = transcribe_audio_file(uploaded)
                    st.session_state[f"transcription_{current_tool}"] = trans
                    st.session_state[f"transcription_file_{current_tool}"] = uploaded.name
            else:
                trans = st.session_state[f"transcription_{current_tool}"]

            if trans:
                st.success("Transcription: " + trans)
                # Overwrite the input box content with the transcription
                st.session_state[input_key] = trans
                # Force rerun to display transcription in text area
                st.experimental_rerun()


    # Send / clear / speak toggle
    speak_pref = st.checkbox("Speak replies aloud", key=f"speak_{current_tool}", value=False)
    colA, colB, colC = st.columns([1,1,1])
    
    with colA:
        if st.button("Send", key=f"send_{current_tool}"):
            # Re-read the current content of the text area
            final_user_text = st.session_state.get(input_key, "").strip()
            
            if not final_user_text:
                st.warning("Write something first!")
            else:
                # 1. Save user msg
                add_user_tool_history(st.session_state.username, current_tool, "user", final_user_text)
                
                # 2. Route and call AI
                with st.spinner("Genie is thinking..."):
                    prompt = route_prompt_for_tool(current_tool, final_user_text)
                    reply = ask_ai_robust(prompt)
                
                # 3. Save reply and speak
                add_user_tool_history(st.session_state.username, current_tool, "assistant", reply)
                if speak_pref and not reply.startswith("❌"):
                    speak_in_browser(reply)
                
                # 4. Clear input and Rerun
                st.session_state[input_key] = ""
                # Clear transcription memory
                if f"transcription_{current_tool}" in st.session_state:
                     del st.session_state[f"transcription_{current_tool}"]
                if f"transcription_file_{current_tool}" in st.session_state:
                     del st.session_state[f"transcription_file_{current_tool}"]

                st.experimental_rerun()
                
    with colB:
        if st.button("Clear history (tool)", key=f"clear_{current_tool}"):
            # FIX: Properly delete the specific tool's history for the user
            if st.session_state.username in chat_history and current_tool in chat_history[st.session_state.username]:
                del chat_history[st.session_state.username][current_tool]
                save_json(CHAT_DB, chat_history)
                st.success(f"History for {current_tool} cleared!")
                st.experimental_rerun()
            else:
                st.info("No history to clear.")

    st.markdown("</div>", unsafe_allow_html=True) # Close the section div

# -----------------------------
# RUN THE UI FOR THE CURRENT TOOL
# -----------------------------

tool_chat_ui()