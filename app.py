# app.py — StudyGenie Pro (Local JSON persistence, no Firebase)
import streamlit as st
import requests, json, time, random, hashlib, os, urllib.parse
from pathlib import Path
from typing import Dict, Any

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="StudyGenie Pro (Local DB)", layout="centered")
DB_PATH = Path("db.json")

# -------------------------
# UTIL: DB (simple JSON file)
# -------------------------
def load_db() -> Dict[str, Any]:
    if DB_PATH.exists():
        try:
            return json.loads(DB_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {"users": {}}
    else:
        return {"users": {}}

def save_db(db: Dict[str, Any]):
    DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

db = load_db()

# -------------------------
# UTIL: user helpers
# -------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_user(username: str, password: str, display_name: str):
    key = username.lower().strip()
    if key in db["users"]:
        return False, "Username already exists."
    db["users"][key] = {
        "password_hash": hash_password(password) if password else None,
        "display_name": display_name or username,
        "profile": {"name": display_name or username, "grade": "", "goal": ""},
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
        return False, "This account is guest-only (no password)."
    if user["password_hash"] != hash_password(password):
        return False, "Incorrect password."
    return True, "OK"

def ensure_guest(username: str, display_name: str):
    key = username.lower().strip()
    if key not in db["users"]:
        db["users"][key] = {
            "password_hash": None,
            "display_name": display_name,
            "profile": {"name": display_name, "grade": "", "goal": ""},
            "chats": [],
            "notes": [],
            "flashcards": [],
            "planner": []
        }
        save_db(db)

# -------------------------
# THEME & CSS (Gen-Z pastel)
# -------------------------
def inject_css(dark=False):
    # lighter palette: sky-blue -> light-purple -> baby-pink
    bg = "linear-gradient(180deg,#dff7ff,#e8d7ff,#ffe6f4)" if not dark else "linear-gradient(180deg,#0f172a,#1f2a44,#2b2540)"
    card_bg = "rgba(255,255,255,0.75)" if not dark else "rgba(255,255,255,0.03)"
    text = "#16121f" if not dark else "#e6e6ff"
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,700;1,600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{
        background: {bg};
        background-attachment: fixed;
        font-family: 'Poppins', sans-serif;
        color: {text};
    }}
    .wide {{ max-width:1100px; margin-left:auto; margin-right:auto; }}
    .card {{
        background: {card_bg};
        padding:18px;
        border-radius:14px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.06);
        margin-bottom:14px;
    }}
    h1 {{ font-weight:700; font-style:italic; }}
    .muted {{ color: rgba(0,0,0,0.45); font-size:12px; }}
    .chat-user {{ background: rgba(0,0,0,0.04); padding:12px; border-radius:12px; margin:6px 0; }}
    .chat-ai {{ background: rgba(255,255,255,0.06); padding:12px; border-radius:12px; margin:6px 0; }}
    .btn {{ border-radius:10px; padding:6px 12px; }}
    .small {{ font-size:12px; color: rgba(0,0,0,0.55);}}
    .pop {{ animation: pop 0.35s ease-out; transform-origin: center; }}
    @keyframes pop {{
      0% {{ transform: scale(0.96); opacity: 0; }}
      100% {{ transform: scale(1); opacity: 1; }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
inject_css(st.session_state.dark_mode)

# -------------------------
# SESSION: login state & last prompt caching
# -------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "last_request" not in st.session_state:
    st.session_state.last_request = None

# -------------------------
# AUTH UI (if not logged in)
# -------------------------
def show_login_ui():
    st.markdown("<div class='wide card pop'>", unsafe_allow_html=True)
    st.title("Welcome to StudyGenie 💞")
    st.write("Login to save chats across sessions. Choose Guest, Create account, or Login.")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Guest")
        guest_name = st.text_input("Nickname (Guest)", value=f"guest{int(time.time())%10000}", key="guest_name")
        if st.button("Continue as Guest"):
            uid = f"guest_{guest_name}_{int(time.time())}"
            ensure_guest(uid, guest_name)
            st.session_state.user = uid
            st.session_state.display_name = guest_name
            st.experimental_rerun()
    with col2:
        st.subheader("Create account / Login")
        tab = st.radio("Action", ["Create", "Login"])
        uname = st.text_input("Username", key="auth_user")
        disp = st.text_input("Display name (optional)", key="auth_display")
        pwd = st.text_input("Password (leave empty for guest)", type="password", key="auth_pwd")
        if tab == "Create":
            if st.button("Create Account"):
                if not uname.strip():
                    st.warning("Username required.")
                else:
                    ok, msg = create_user(uname.strip(), pwd or "", disp or uname.strip())
                    if ok:
                        st.success(msg)
                        st.session_state.user = uname.strip().lower()
                        st.session_state.display_name = disp or uname.strip()
                        st.experimental_rerun()
                    else:
                        st.error(msg)
        else:
            if st.button("Login"):
                if not uname.strip():
                    st.warning("Username required.")
                else:
                    ok, msg = verify_user(uname.strip(), pwd or "")
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
    show_login_ui()

# Now user is set
username = st.session_state.user
display_name = st.session_state.get("display_name", username)

# ensure user exists in db
ensure_guest(username, display_name)
# load user data into session if not already
if "loaded_user" not in st.session_state or st.session_state.loaded_user != username:
    user_data = db["users"].get(username.lower()) or db["users"].get(username) or db["users"].get(username.lower().strip())
    if user_data:
        st.session_state.chat_history = user_data.get("chats", [])
        st.session_state.notes_store = user_data.get("notes", [])
        st.session_state.flashcards = user_data.get("flashcards", [])
        st.session_state.planner = user_data.get("planner", [])
        st.session_state.profile = user_data.get("profile", {"name": display_name, "grade": "", "goal": ""})
    else:
        # safety fallback
        st.session_state.chat_history = []
        st.session_state.notes_store = []
        st.session_state.flashcards = []
        st.session_state.planner = []
        st.session_state.profile = {"name": display_name, "grade": "", "goal": ""}
    st.session_state.loaded_user = username

# -------------------------
# ROBUST OPENAI CALL (requests, retries, safe parse)
# -------------------------
def ask_openai(prompt: str, model="gpt-4o-mini", temp=0.45, max_retries=2) -> str:
    # cache duplicate requests to avoid spamming
    if st.session_state.last_request == prompt and prompt.strip():
        return "⚠️ Duplicate request blocked. Modify prompt or try a different tool."
    key = st.secrets.get("OPENAI_API_KEY")
    if not key:
        return "❌ No OPENAI_API_KEY found in Streamlit Secrets."
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are StudyGenie, a concise friendly study assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temp,
        "max_tokens": 700
    }
    attempt = 0
    while attempt <= max_retries:
        attempt += 1
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=30)
        except Exception as e:
            if attempt > max_retries:
                return f"❌ Network error: {e}"
            time.sleep(1.0); continue
        try:
            rj = r.json()
        except Exception as e:
            if attempt > max_retries:
                return f"❌ Invalid JSON response: {e}"
            time.sleep(0.8); continue
        if "error" in rj:
            err_msg = rj["error"].get("message", str(rj["error"]))
            if attempt <= max_retries and (r.status_code >= 500 or "rate limit" in err_msg.lower()):
                time.sleep(1.2); continue
            return f"❌ AI error: {err_msg}"
        choices = rj.get("choices")
        if not choices:
            if attempt <= max_retries:
                time.sleep(0.6); continue
            return "❌ AI returned no choices. Try again."
        msg = choices[0].get("message") or {}
        content = msg.get("content") or msg.get("text") or ""
        if not content and attempt <= max_retries:
            time.sleep(0.6); continue
        st.session_state.last_request = prompt
        return content or "❌ Empty response from AI."
    return "❌ Failed after retries."

# -------------------------
# UI HEADER / Logout / Dark mode
# -------------------------
inject_css(st.session_state.dark_mode)
st.markdown("<div class='wide'>", unsafe_allow_html=True)
c1, c2 = st.columns([4,1])
with c1:
    st.markdown(f"**Signed in as:** {display_name}")
    st.markdown("<div class='small muted'>Local-saved chats • Guest or account login • Add OPENAI_API_KEY in Secrets</div>", unsafe_allow_html=True)
with c2:
    if st.button("🌙 Dark" if not st.session_state.dark_mode else "🌤️ Light"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        inject_css(st.session_state.dark_mode)
        st.experimental_rerun()
    if st.button("Logout"):
        # persist user data and logout
        db["users"][username.lower()] = {
            "password_hash": db["users"][username.lower()].get("password_hash"),
            "display_name": st.session_state.profile.get("name", display_name),
            "profile": st.session_state.profile,
            "chats": st.session_state.chat_history,
            "notes": st.session_state.notes_store,
            "flashcards": st.session_state.flashcards,
            "planner": st.session_state.planner
        }
        save_db(db)
        for k in ["user","display_name","loaded_user","last_request"]:
            if k in st.session_state: del st.session_state[k]
        st.experimental_rerun()
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# NAV + Quick buttons (1..5)
# -------------------------
col1, col2, col3, col4, col5 = st.columns(5)
if col1.button("1️⃣ Doubt"): page="Doubt"
elif col2.button("2️⃣ Flashcards"): page="Flashcards"
elif col3.button("3️⃣ Notes"): page="Notes"
elif col4.button("4️⃣ Planner"): page="Planner"
elif col5.button("5️⃣ Boost"): page="Boost"
else:
    page = st.sidebar.selectbox("Go to", ["Doubt","Flashcards","Notes","Summary","AnswerChecker","Planner","Voice","Saved","Profile","Boost"])

# -------------------------
# PAGE: Doubt Solver
# -------------------------
if page == "Doubt":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("💡 AI Doubt Solver")
    q = st.text_area("Ask your question:", key="doubt_in")
    if st.button("Solve"):
        if q.strip():
            with st.spinner("Thinking..."):
                ans = ask_openai(q)
            st.session_state.chat_history.append({"role":"user","text":q,"time":int(time.time())})
            st.session_state.chat_history.append({"role":"ai","text":ans,"time":int(time.time())})
            # update db and persist
            db["users"][username.lower()]["chats"] = st.session_state.chat_history
            save_db(db)
            st.markdown("**Answer:**"); st.write(ans)
        else:
            st.warning("Ask something first!")
    if st.checkbox("Show chat history"):
        for msg in reversed(st.session_state.chat_history[-50:]):
            cls = "chat-user" if msg["role"]=="user" else "chat-ai"
            st.markdown(f"<div class='{cls}'>{msg['text']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PAGE: Flashcards
# -------------------------
elif page == "Flashcards":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("🃏 Flashcards")
    topic = st.text_input("Topic for cards:")
    cnt = st.slider("Cards", 3, 20, 6)
    if st.button("Generate"):
        if topic.strip():
            raw = ask_openai(f"Create {cnt} Q/A flashcards for: {topic}. Label with Q: and A:")
            cards=[]
            qtmp=None
            for line in raw.splitlines():
                line=line.strip()
                if line.lower().startswith("q:"):
                    qtmp=line.split(":",1)[1].strip()
                elif line.lower().startswith("a:") and qtmp:
                    a=line.split(":",1)[1].strip()
                    cards.append({"q":qtmp,"a":a}); qtmp=None
            if not cards:
                parts=[p.strip() for p in raw.split("\n\n") if p.strip()]
                for p in parts:
                    if ":" in p:
                        k,v=p.split(":",1); cards.append({"q":k.strip()[:200],"a":v.strip()})
            st.session_state.flashcards = cards
            # persist
            db["users"][username.lower()]["flashcards"] = st.session_state.flashcards
            save_db(db)
            st.success(f"Created {len(cards)} cards.")
        else:
            st.warning("Enter topic.")
    if st.session_state.get("flashcards"):
        idx = st.number_input("Card index", 1, max(1,len(st.session_state.flashcards)), 1)
        card = st.session_state.flashcards[idx-1]
        st.markdown(f"**Q:** {card['q']}")
        if st.button("Show Answer"):
            st.markdown(f"**A:** {card['a']}")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PAGE: Notes
# -------------------------
elif page == "Notes":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("📝 Notes Generator & Save")
    topic = st.text_input("Topic:")
    if st.button("Generate Notes"):
        if topic.strip():
            out = ask_openai(f"Create concise class notes for: {topic}. Use bullets and 1 short example.")
            st.text_area("Generated notes", value=out, height=260, key="gen_notes_area")
        else:
            st.warning("Enter topic.")
    if st.session_state.get("gen_notes_area"):
        if st.button("Save Notes"):
            st.session_state.notes_store.append({"title": topic or "Untitled", "content": st.session_state.get("gen_notes_area")})
            db["users"][username.lower()]["notes"] = st.session_state.notes_store
            save_db(db)
            st.success("Saved.")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PAGE: Summary / Brain-dump cleaner
# -------------------------
elif page == "Summary":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("🧠 Brain-dump Cleaner")
    messy = st.text_area("Paste messy notes / ideas:")
    if st.button("Clean"):
        if messy.strip():
            out = ask_openai(f"Organize and clean this into titled sections and action items:\n{messy}")
            st.write(out)
            st.session_state.chat_history.append({"role":"user","text":"Cleaned brain dump","time":int(time.time())})
            st.session_state.chat_history.append({"role":"ai","text":out,"time":int(time.time())})
            db["users"][username.lower()]["chats"] = st.session_state.chat_history
            save_db(db)
        else:
            st.warning("Paste something.")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PAGE: Answer Checker
# -------------------------
elif page == "AnswerChecker":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("✅ Answer Checker")
    q = st.text_input("Question:")
    student = st.text_area("Student's answer:")
    if st.button("Check"):
        if q.strip() and student.strip():
            out = ask_openai(f"Question: {q}\nStudent answer: {student}\nGive a score /10 and short feedback.")
            st.write(out)
            st.session_state.chat_history.append({"role":"user","text":"Checked answer","time":int(time.time())})
            st.session_state.chat_history.append({"role":"ai","text":out,"time":int(time.time())})
            db["users"][username.lower()]["chats"] = st.session_state.chat_history
            save_db(db)
        else:
            st.warning("Fill both fields.")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PAGE: Planner
# -------------------------
elif page == "Planner":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("📆 Planner")
    task = st.text_input("New task:")
    when = st.text_input("When (optional):")
    if st.button("Add Task"):
        if task.strip():
            st.session_state.planner.append({"task":task,"when":when})
            db["users"][username.lower()]["planner"] = st.session_state.planner
            save_db(db)
            st.success("Added.")
        else:
            st.warning("Enter a task.")
    if st.session_state.planner:
        for i,t in enumerate(st.session_state.planner,1):
            st.write(f"{i}. {t['task']} — {t['when']}")
        if st.button("Generate 7-day plan"):
            prompt = "Create a 7-day study schedule from these tasks:\n" + "\n".join([p["task"] for p in st.session_state.planner])
            out = ask_openai(prompt)
            st.write(out)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PAGE: Voice (upload -> transcribe)
# -------------------------
elif page == "Voice":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("🎤 Voice Input (optional)")
    audio = st.file_uploader("Upload audio (mp3/m4a/wav)", type=["mp3","m4a","wav"])
    if audio and st.button("Transcribe & Answer"):
        key = st.secrets.get("OPENAI_API_KEY")
        if not key:
            st.error("Add OPENAI_API_KEY to Streamlit Secrets to use transcription.")
        else:
            try:
                files = {"file": (audio.name, audio.getvalue())}
                data = {"model":"gpt-4o-transcribe"}  # or your available transcription model
                headers = {"Authorization": f"Bearer {key}"}
                res = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=90)
                rj = res.json()
                if "error" in rj:
                    st.error("Transcription error: " + str(rj["error"].get("message","")))
                else:
                    text = rj.get("text","")
                    st.write("Transcribed text:")
                    st.write(text)
                    out = ask_openai("Answer based on transcript:\n" + text)
                    st.write("AI answer:")
                    st.write(out)
            except Exception as e:
                st.error("Transcription failed: " + str(e))
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PAGE: Saved (notes & chats)
# -------------------------
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
        for msg in st.session_state.chat_history[-50:][::-1]:
            who = "You" if msg["role"]=="user" else "StudyGenie"
            st.write(f"**{who}:** {msg['text']}")
        if st.button("Download chat JSON"):
            st.download_button("Download", json.dumps(st.session_state.chat_history, ensure_ascii=False, indent=2), file_name=f"chats_{username}.json")
    else:
        st.info("No chats.")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PAGE: Profile
# -------------------------
elif page == "Profile":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("👤 Profile")
    name = st.text_input("Display name", value=st.session_state.profile.get("name", display_name))
    grade = st.text_input("Grade", value=st.session_state.profile.get("grade",""))
    goal = st.text_input("Short goal (ex: Study in Korea)", value=st.session_state.profile.get("goal",""))
    if st.button("Save profile"):
        st.session_state.profile.update({"name": name, "grade": grade, "goal": goal})
        # persist
        db["users"][username.lower()]["profile"] = st.session_state.profile
        db["users"][username.lower()]["display_name"] = name
        save_db(db)
        st.success("Profile saved.")
    st.write(st.session_state.profile)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PAGE: Boost
# -------------------------
elif page == "Boost":
    st.markdown("<div class='card pop'>", unsafe_allow_html=True)
    st.subheader("💖 Motivation Booster")
    mega = [
        "Bestie you're UNSTOPPABLE 🔥","Your future self is proud 💗","Glow-up loading ✨",
        "Small steps = massive glow-up","Korean apartment vibes loading…","Discipline looks cute on you",
        "One study session today = big flex tomorrow","You are literally iconic"
    ]
    if st.button("Boost me"):
        st.success(random.choice(mega))
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Persist current session user data to db at end (best-effort)
# -------------------------
db["users"][username.lower()]["chats"] = st.session_state.chat_history
db["users"][username.lower()]["notes"] = st.session_state.notes_store
db["users"][username.lower()]["flashcards"] = st.session_state.flashcards
db["users"][username.lower()]["planner"] = st.session_state.planner
db["users"][username.lower()]["profile"] = st.session_state.profile
db["users"][username.lower()]["display_name"] = st.session_state.profile.get("name", display_name)
save_db(db)

# -------------------------
# Footer
# -------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; font-size:12px; color:rgba(0,0,0,0.55)'>StudyGenie Pro • Local-saved chats • Made with ❤️</div>", unsafe_allow_html=True)