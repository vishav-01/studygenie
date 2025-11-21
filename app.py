# app.py — StudyGenie Ultra (Upgraded: robust AI, SRS flashcards, planner, voice, local persistence)
import streamlit as st
import requests, json, time, random, hashlib, os
from pathlib import Path
from typing import Dict, Any

# ---------------- CONFIG ----------------
st.set_page_config(page_title="StudyGenie Ultra", layout="centered")
DB_PATH = Path("db.json")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------------- SIMPLE JSON DB ----------------
def load_db() -> Dict[str, Any]:
    if DB_PATH.exists():
        try:
            return json.loads(DB_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {"users": {}}
    return {"users": {}}

def save_db(db: Dict[str, Any]):
    DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

db = load_db()

# ---------------- UTIL: auth helpers ----------------
def sha256(x: str) -> str:
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

def create_user(username: str, password: str, display: str):
    key = username.lower().strip()
    if not key:
        return False, "Username required."
    if key in db["users"]:
        return False, "Username exists."
    db["users"][key] = {
        "password_hash": sha256(password) if password else None,
        "display_name": display or username,
        "profile": {"name": display or username, "grade": "", "goal": ""},
        "chats": [],
        "notes": [],
        "flashcards": [],
        "planner": []
    }
    save_db(db)
    return True, "Account created."

def verify_user(username: str, password: str):
    key = username.lower().strip()
    user = db["users"].get(key)
    if not user:
        return False, "User not found."
    if user["password_hash"] is None:
        return False, "Account has no password (guest)."
    if user["password_hash"] != sha256(password):
        return False, "Incorrect password."
    return True, "OK"

def ensure_guest(username: str, display: str):
    key = username.lower().strip()
    if key not in db["users"]:
        db["users"][key] = {
            "password_hash": None,
            "display_name": display,
            "profile": {"name": display, "grade": "", "goal": ""},
            "chats": [],
            "notes": [],
            "flashcards": [],
            "planner": []
        }
        save_db(db)

# ---------------- THEME & CSS ----------------
def inject_css(dark=False):
    if not dark:
        bg = "linear-gradient(180deg,#bfefff,#e7d8ff,#ffddee)"  # sky blue -> light purple -> baby pink
        card_bg = "rgba(255,255,255,0.86)"
        text = "#121020"
    else:
        bg = "linear-gradient(180deg,#0f172a,#1f2a44,#2b2540)"
        card_bg = "rgba(255,255,255,0.03)"
        text = "#e6e6ff"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,700;1,600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{
        background: {bg};
        background-attachment: fixed;
        font-family: 'Poppins', sans-serif;
        color: {text};
    }}
    .wide{{max-width:1100px; margin-left:auto; margin-right:auto;}}
    .card{{background:{card_bg}; padding:18px; border-radius:14px; box-shadow:0 6px 30px rgba(0,0,0,0.06); margin-bottom:14px;}}
    h1{{font-weight:700; font-style:italic;}}
    .muted{{color: rgba(0,0,0,0.45); font-size:12px;}}
    .chat-user{{background: rgba(0,0,0,0.04); padding:12px; border-radius:12px; margin:6px 0;}}
    .chat-ai{{background: rgba(255,255,255,0.06); padding:12px; border-radius:12px; margin:6px 0;}}
    .pop{{animation: pop 0.35s ease-out; transform-origin:center;}}
    @keyframes pop{{0%{{transform:scale(0.96);opacity:0}}100%{{transform:scale(1);opacity:1}}}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
inject_css(st.session_state.dark_mode)

# ---------------- SESSION STATE defaults ----------------
if "user" not in st.session_state:
    st.session_state.user = None
if "last_request" not in st.session_state:
    st.session_state.last_request = None

# ---------------- ROBUST OPENAI CALL ----------------
def ask_openai(prompt: str,
               preferred_model: str = "gpt-4o-mini",
               fallback_model: str = "gpt-3.5-turbo",
               temperature: float = 0.2,
               max_retries: int = 2) -> str:
    """
    Robust call to OpenAI Chat Completions with retries, backoff, fallback model,
    and safe JSON parsing. Returns string (error message begins with ❌).
    Also enforces a system prompt to return short crisp notes where applicable.
    """
    # Avoid duplicate rapid re-requests for same prompt
    if st.session_state.get("last_request") == prompt and prompt.strip():
        return "⚠️ Duplicate request blocked. Modify your prompt slightly."

    key = st.secrets.get("OPENAI_API_KEY")
    if not key:
        return "❌ Missing OPENAI_API_KEY in Streamlit Secrets."

    system_note = "You are StudyGenie, a concise study assistant. Always answer in short, clear bullet points or 2-4 short sentences unless user asks otherwise. Keep it crisp and student-friendly."

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    models_to_try = [preferred_model, fallback_model]

    for model in models_to_try:
        attempt = 0
        while attempt <= max_retries:
            attempt += 1
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_note},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": 600
            }
            try:
                r = requests.post("https://api.openai.com/v1/chat/completions",
                                  headers=headers,
                                  json=payload,
                                  timeout=25)
            except Exception as e:
                if attempt > max_retries:
                    return f"❌ Network error: {e}"
                time.sleep(0.9 * attempt)
                continue

            # parse JSON safely
            try:
                rj = r.json()
            except Exception as e:
                if attempt > max_retries:
                    return f"❌ Invalid JSON from AI: {e}"
                time.sleep(0.6); continue

            # errors from API
            if "error" in rj:
                msg = rj["error"].get("message", str(rj["error"]))
                # retry on server errors or rate limits
                if attempt <= max_retries and (r.status_code >= 500 or "rate limit" in msg.lower()):
                    time.sleep(1.2); continue
                # otherwise return error text
                return f"❌ AI error: {msg}"

            choices = rj.get("choices")
            if not choices:
                if attempt <= max_retries:
                    time.sleep(0.6); continue
                # try next model
                break

            # attempt to extract content
            first = choices[0]
            msg = first.get("message") or {}
            content = msg.get("content") or msg.get("text") or ""
            if not content:
                if attempt <= max_retries:
                    time.sleep(0.6); continue
                break

            # success
            st.session_state.last_request = prompt
            # Make answers crisp: trim extra whitespace
            return content.strip()

    # If we got here, no model succeeded
    return "❌ AI did not return a valid response. Try again in a moment."

# ---------------- AUTH UI (Guest / Create / Login) ----------------
def auth_ui():
    st.markdown("<div class='wide card pop'>", unsafe_allow_html=True)
    st.title("Welcome to StudyGenie Ultra")
    st.write("Sign in to save chats locally. You can use Guest or create a free local account.")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Guest")
        guest_name = st.text_input("Guest display name", value=f"Guest{int(time.time())%10000}", key="guest_name")
        if st.button("Continue as Guest"):
            uid = f"guest_{guest_name}_{int(time.time())}"
            ensure_guest(uid, guest_name)
            st.session_state.user = uid
            st.session_state.display_name = guest_name
            st.experimental_rerun()
    with col2:
        st.subheader("Create account / Login")
        mode = st.radio("Action", ["Create", "Login"], key="auth_mode")
        uname = st.text_input("Username", key="auth_user")
        display = st.text_input("Display name (optional)", key="auth_display")
        pwd = st.text_input("Password", type="password", key="auth_pwd")
        if mode == "Create":
            if st.button("Create Account"):
                if not uname.strip():
                    st.warning("Enter a username.")
                else:
                    ok, msg = create_user(uname.strip().lower(), pwd or "", display or uname.strip())
                    if ok:
                        st.success("Account created. You are logged in.")
                        st.session_state.user = uname.strip().lower()
                        st.session_state.display_name = display or uname.strip()
                        st.experimental_rerun()
                    else:
                        st.error(msg)
        else:
            if st.button("Login"):
                if not uname.strip():
                    st.warning("Enter username.")
                else:
                    ok, msg = verify_user(uname.strip().lower(), pwd or "")
                    if ok:
                        st.success("Logged in.")
                        st.session_state.user = uname.strip().lower()
                        st.session_state.display_name = db["users"][uname.strip().lower()].get("display_name", uname.strip())
                        st.experimental_rerun()
                    else:
                        st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if st.session_state.user is None:
    auth_ui()

# ---------------- load user data into session ----------------
username = st.session_state.user
display_name = st.session_state.get("display_name", username)
ensure_guest(username, display_name)

if "loaded_for" not in st.session_state or st.session_state.loaded_for != username:
    user_data = db["users"].get(username.lower()) or {}
    st.session_state.chat_history = user_data.get("chats", [])
    st.session_state.notes_store = user_data.get("notes", [])
    st.session_state.flashcards = user_data.get("flashcards", [])
    st.session_state.planner = user_data.get("planner", [])
    st.session_state.profile = user_data.get("profile", {"name": display_name, "grade": "", "goal": ""})
    st.session_state.loaded_for = username

# ---------------- HEADER ----------------
inject_css(st.session_state.dark_mode)
st.markdown("<div class='wide'>", unsafe_allow_html=True)
c1, c2 = st.columns([4,1])
with c1:
    st.markdown(f"**Signed in as:** {display_name}")
    st.markdown("<div class='muted'>Local-saved chats • Guest or local account</div>", unsafe_allow_html=True)
with c2:
    if st.button("🌙 Dark" if not st.session_state.dark_mode else "🌤️ Light"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        inject_css(st.session_state.dark_mode)
        st.experimental_rerun()
    if st.button("Logout"):
        # persist and clear
        db["users"][username.lower()]["chats"] = st.session_state.chat_history
        db["users"][username.lower()]["notes"] = st.session_state.notes_store
        db["users"][username.lower()]["flashcards"] = st.session_state.flashcards
        db["users"][username.lower()]["planner"] = st.session_state.planner
        db["users"][username.lower()]["profile"] = st.session_state.profile
        db["users"][username.lower()]["display_name"] = st.session_state.profile.get("name", display_name)
        save_db(db)
        for k in ["user","display_name","loaded_for","last_request"]:
            if k in st.session_state: del st.session_state[k]
        st.experimental_rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- NAV QUICK BUTTONS ----------------
col1, col2, col3, col4, col5 = st.columns(5)
if col1.button("1️⃣ Doubt"): page="Doubt"
elif col2.button("2️⃣ Flashcards"): page="Flashcards"
elif col3.button("3️⃣ Notes"): page="Notes"
elif col4.button("4️⃣ Planner"): page="Planner"
elif col5.button("5️⃣ Boost"): page="Boost"
else:
    page = st.sidebar.selectbox("Go to", ["Doubt","Flashcards","Notes","Summary","AnswerChecker","Planner","Voice","Saved","Profile","Boost"])

# ---------------- DOUBT SOLVER ----------------
if page == "Doubt":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("💡 AI Doubt Solver")
    q = st.text_area("Type your question (ask clearly):", key="doubt_in")
    if st.button("Solve"):
        if q.strip():
            with st.spinner("Thinking..."):
                ans = ask_openai(q)
            st.session_state.chat_history.append({"role":"user","text":q,"time":int(time.time())})
            st.session_state.chat_history.append({"role":"ai","text":ans,"time":int(time.time())})
            # persist
            db["users"][username.lower()]["chats"] = st.session_state.chat_history
            save_db(db)
            st.markdown("**Answer (crispy):**")
            st.write(ans)
        else:
            st.warning("Please type a question.")
    if st.checkbox("Show chat history"):
        for msg in reversed(st.session_state.chat_history[-60:]):
            cls = "chat-user" if msg["role"]=="user" else "chat-ai"
            st.markdown(f"<div class='{cls}'>{msg['text']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FLASHCARDS w/ tiny SRS ----------------
elif page == "Flashcards":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("🃏 Flashcards (Generate & Review)")
    topic = st.text_input("Topic for cards:", key="fc_topic")
    cnt = st.slider("Cards", 3, 20, 6, key="fc_cnt")
    if st.button("Generate Cards"):
        if topic.strip():
            raw = ask_openai(f"Create {cnt} concise Q/A flashcards for: {topic}. Use lines starting with Q: and A:")
            # parse
            cards=[]
            qtmp=None
            for line in raw.splitlines():
                line=line.strip()
                if line.lower().startswith("q:"):
                    qtmp=line.split(":",1)[1].strip()
                elif line.lower().startswith("a:") and qtmp:
                    a=line.split(":",1)[1].strip()
                    cards.append({"q":qtmp,"a":a,"ease":2.5,"interval":1,"reviews":0})
                    qtmp=None
            if not cards:
                parts=[p.strip() for p in raw.split("\n\n") if p.strip()]
                for p in parts:
                    if ":" in p:
                        k,v=p.split(":",1); cards.append({"q":k.strip()[:200],"a":v.strip(),"ease":2.5,"interval":1,"reviews":0})
            st.session_state.flashcards = cards
            db["users"][username.lower()]["flashcards"] = st.session_state.flashcards
            save_db(db)
            st.success(f"Created {len(cards)} cards.")
        else:
            st.warning("Enter topic.")
    # Review mode
    if st.session_state.get("flashcards"):
        st.markdown("**Review mode**")
        # pick due card roughly (simple due by reviews)
        idx = 0
        if len(st.session_state.flashcards) > 1:
            idx = random.randint(0, len(st.session_state.flashcards)-1)
        card = st.session_state.flashcards[idx]
        st.markdown(f"**Q:** {card['q']}")
        if st.button("Show Answer"):
            st.markdown(f"**A:** {card['a']}")
            colc = st.columns(3)
            if colc[0].button("Easy"):
                # simple SRS: increase interval and ease
                card["reviews"] += 1
                card["interval"] = int(card.get("interval",1) * 2)
                card["ease"] = min(3.5, card.get("ease",2.5) + 0.2)
                st.success("Marked Easy. Will show later.")
            if colc[1].button("Good"):
                card["reviews"] += 1
                card["interval"] = int(card.get("interval",1) * 1.5) or 1
                st.success("Marked Good.")
            if colc[2].button("Hard"):
                card["reviews"] += 1
                card["interval"] = max(1, int(card.get("interval",1) * 0.7))
                card["ease"] = max(1.3, card.get("ease",2.5) - 0.2)
                st.success("Marked Hard — will repeat sooner.")
            # persist after marking
            db["users"][username.lower()]["flashcards"] = st.session_state.flashcards
            save_db(db)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- NOTES generator & save ----------------
elif page == "Notes":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("📝 Notes Generator & Save")
    topic = st.text_input("Topic:", key="notes_topic")
    if st.button("Generate Notes"):
        if topic.strip():
            out = ask_openai(f"Create short, crisp class notes for: {topic}. Use bullet points and 3-4 lines max.")
            st.text_area("Generated notes", value=out, height=260, key="gen_notes_out")
        else:
            st.warning("Enter a topic.")
    if st.session_state.get("gen_notes_out"):
        if st.button("Save Notes"):
            st.session_state.notes_store.append({"title": topic or "Untitled", "content": st.session_state.get("gen_notes_out")})
            db["users"][username.lower()]["notes"] = st.session_state.notes_store
            save_db(db)
            st.success("Saved.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- BRAIN-DUMP CLEANER (Summary) ----------------
elif page == "Summary":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("🧠 Brain-dump Cleaner")
    messy = st.text_area("Paste messy notes / ideas:")
    if st.button("Clean & Organize"):
        if messy.strip():
            out = ask_openai(f"Organize this into titled sections, bullets, and 3 action items:\n{messy}")
            st.write(out)
            st.session_state.chat_history.append({"role":"user","text":"Brain-dump cleaned","time":int(time.time())})
            st.session_state.chat_history.append({"role":"ai","text":out,"time":int(time.time())})
            db["users"][username.lower()]["chats"] = st.session_state.chat_history
            save_db(db)
        else:
            st.warning("Paste something.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ANSWER CHECKER ----------------
elif page == "AnswerChecker":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("✅ Answer Checker")
    question = st.text_input("Question:")
    student_answer = st.text_area("Student's answer:")
    if st.button("Check Answer"):
        if question.strip() and student_answer.strip():
            prompt = f"Question:\n{question}\n\nStudent's answer:\n{student_answer}\n\nGive a score out of 10 and concise corrections. Keep it short."
            out = ask_openai(prompt)
            st.write(out)
            st.session_state.chat_history.append({"role":"user","text":"Answer checked","time":int(time.time())})
            st.session_state.chat_history.append({"role":"ai","text":out,"time":int(time.time())})
            db["users"][username.lower()]["chats"] = st.session_state.chat_history
            save_db(db)
        else:
            st.warning("Add question and answer.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- PLANNER (tasks + AI 7-day plan) ----------------
elif page == "Planner":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("📅 Planner")
    task = st.text_input("New task:")
    when = st.text_input("Deadline / date (optional):")
    if st.button("Add Task"):
        if task.strip():
            st.session_state.planner.append({"task":task,"when":when})
            db["users"][username.lower()]["planner"] = st.session_state.planner
            save_db(db)
            st.success("Task added.")
        else:
            st.warning("Enter a task.")
    if st.session_state.planner:
        st.write("Your tasks:")
        for i,t in enumerate(st.session_state.planner,1):
            st.write(f"{i}. {t['task']} — {t['when']}")
        if st.button("Generate 7-day study plan"):
            prompt = "Create a 7-day study plan using these tasks:\n" + "\n".join([p["task"] for p in st.session_state.planner])
            with st.spinner("Generating plan..."):
                plan = ask_openai(prompt)
            st.success("Study Plan:")
            st.write(plan)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- VOICE (upload -> transcribe via OpenAI) ----------------
elif page == "Voice":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("🎤 Voice Input (upload to transcribe)")
    audio_file = st.file_uploader("Upload audio (mp3/m4a/wav)", type=["mp3","m4a","wav"])
    if audio_file and st.button("Transcribe & Answer"):
        key = st.secrets.get("OPENAI_API_KEY")
        if not key:
            st.error("Add OPENAI_API_KEY to Streamlit Secrets to use transcription.")
        else:
            try:
                files = {"file": (audio_file.name, audio_file.getvalue())}
                data = {"model":"gpt-4o-transcribe"}
                headers = {"Authorization": f"Bearer {key}"}
                resp = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=90)
                rj = resp.json()
                if "error" in rj:
                    st.error("Transcription error: " + str(rj["error"].get("message","")))
                else:
                    text = rj.get("text","")
                    st.write("Transcribed text:")
                    st.write(text)
                    out = ask_openai("Answer concisely based on the transcript:\n" + text)
                    st.write("AI answer:")
                    st.write(out)
            except Exception as e:
                st.error("Transcription failed: " + str(e))
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SAVED (notes & chats) ----------------
elif page == "Saved":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("💾 Saved Notes & Chats")
    if st.session_state.notes_store:
        for i,n in enumerate(st.session_state.notes_store,1):
            with st.expander(f"{i}. {n['title']}"):
                st.write(n["content"])
                st.download_button(f"Download {n['title']}", n["content"], file_name=f"{n['title']}.txt")
    else:
        st.info("No saved notes.")
    if st.session_state.chat_history:
        st.write("Recent chats (latest first):")
        for msg in st.session_state.chat_history[-100:][::-1]:
            who = "You" if msg["role"]=="user" else "StudyGenie"
            st.write(f"**{who}:** {msg['text']}")
        if st.button("Download chat JSON"):
            st.download_button("Download", json.dumps(st.session_state.chat_history, ensure_ascii=False, indent=2), file_name=f"chats_{username}.json")
    else:
        st.info("No chats.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- PROFILE ----------------
elif page == "Profile":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("👤 Profile")
    name = st.text_input("Display name", value=st.session_state.profile.get("name", display_name))
    grade = st.text_input("Grade / Year", value=st.session_state.profile.get("grade",""))
    goal = st.text_input("Short goal", value=st.session_state.profile.get("goal",""))
    if st.button("Save profile"):
        st.session_state.profile.update({"name": name, "grade": grade, "goal": goal})
        db["users"][username.lower()]["profile"] = st.session_state.profile
        db["users"][username.lower()]["display_name"] = name
        save_db(db)
        st.success("Profile saved.")
    st.write(st.session_state.profile)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- MOTIVATION BOOSTER ----------------
elif page == "Boost":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("💖 Motivation Booster")
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
        "Every page you study rewrites your future beautifully."
    ]
    if st.button("Give me motivation"):
        st.success(random.choice(quotes))
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Persist session to db at end ----------------
db["users"][username.lower()]["chats"] = st.session_state.chat_history
db["users"][username.lower()]["notes"] = st.session_state.notes_store
db["users"][username.lower()]["flashcards"] = st.session_state.flashcards
db["users"][username.lower()]["planner"] = st.session_state.planner
db["users"][username.lower()]["profile"] = st.session_state.profile
db["users"][username.lower()]["display_name"] = st.session_state.profile.get("name", display_name)
save_db(db)

# ---------------- Footer ----------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; font-size:12px; color:rgba(0,0,0,0.55)'>StudyGenie Ultra • Local-saved • Made with ❤️</div>", unsafe_allow_html=True)