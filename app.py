# app.py — StudyGenie Pro (stable, persistent chats, guest + optional Google login)
import streamlit as st
import requests, json, os, time, random, urllib.parse
from pathlib import Path

# ----------------- CONFIG -----------------
st.set_page_config(page_title="StudyGenie Pro v3", layout="centered")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ----------------- CSS & THEME (lighter gradient + font) -----------------
def inject_css(dark=False):
    if dark:
        bg = "linear-gradient(180deg,#0f172a,#1f2a44,#2b2540)"
        card_bg = "rgba(255,255,255,0.03)"
        text_col = "#e6e6ff"
    else:
        # sky blue -> light purple -> baby pink (lighter)
        bg = "linear-gradient(180deg,#dff7ff,#e8d7ff,#ffe6f4)"
        card_bg = "rgba(255,255,255,0.8)"
        text_col = "#18122b"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,700;1,600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{
        background: {bg};
        background-attachment: fixed;
        font-family: 'Poppins', sans-serif;
        color: {text_col};
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
    .small-muted {{ color: rgba(0,0,0,0.45); font-size:12px; }}
    .chat-user {{ background: rgba(0,0,0,0.06); padding:12px; border-radius:12px; margin:6px 0; }}
    .chat-ai {{ background: rgba(255,255,255,0.06); padding:12px; border-radius:12px; margin:6px 0; }}
    .btn { border-radius:10px; padding:6px 12px; }
    .top-row { display:flex; justify-content:space-between; align-items:center; gap:12px; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# init dark toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
inject_css(st.session_state.dark_mode)

# ----------------- HELPERS: persistence -----------------
def user_file(username: str):
    safe = urllib.parse.quote_plus(username)
    return DATA_DIR / f"{safe}_chats.json"

def load_chats(username: str):
    p = user_file(username)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_chats(username: str, chats):
    p = user_file(username)
    p.write_text(json.dumps(chats, ensure_ascii=False, indent=2), encoding="utf-8")

# ----------------- AUTH (Guest + Optional Google OAuth) -----------------
def google_oauth_start():
    # requires GOOGLE_CLIENT_ID in st.secrets and redirect URI configured in Google Console
    client_id = st.secrets.get("GOOGLE_CLIENT_ID")
    redirect_uri = st.secrets.get("REDIRECT_URI")  # must match your app URL + callback
    if not client_id or not redirect_uri:
        return None
    scope = urllib.parse.quote("openid email profile")
    state = "sgstate"  # could be random
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&response_type=code&scope={scope}&access_type=offline&state={state}&redirect_uri={urllib.parse.quote(redirect_uri)}"
    )
    return auth_url

def google_exchange_code(code):
    client_id = st.secrets.get("GOOGLE_CLIENT_ID")
    client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = st.secrets.get("REDIRECT_URI")
    if not (client_id and client_secret and redirect_uri):
        return None, "Google OAuth not configured in secrets."
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    try:
        r = requests.post(token_url, data=data, timeout=15)
        rj = r.json()
        if "error" in rj:
            return None, rj.get("error_description", str(rj.get("error")))
        access_token = rj.get("access_token")
        # fetch userinfo
        ui = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {access_token}"}, timeout=15).json()
        email = ui.get("email")
        name = ui.get("name") or email.split("@")[0]
        return {"email": email, "name": name}, None
    except Exception as e:
        return None, str(e)

# Check for callback code in query params
qp = st.experimental_get_query_params()
if "code" in qp and "auth" in qp and qp.get("auth")[0] == "google":
    code = qp.get("code")[0]
    userinfo, err = google_exchange_code(code)
    if userinfo:
        st.session_state.user = userinfo["email"]
        st.session_state.display_name = userinfo.get("name", st.session_state.user)
        st.experimental_set_query_params()  # clear params
    else:
        st.sidebar.error(f"Google login failed: {err}")
        st.experimental_set_query_params()

# If no user in session, show login screen
if "user" not in st.session_state:
    st.markdown("<div class='wide card'>", unsafe_allow_html=True)
    st.title("Welcome to StudyGenie 💞")
    st.write("Login to save your chats or continue as Guest.")
    col1, col2 = st.columns(2)
    with col1:
        guest_name = st.text_input("Enter a display name (Guest):", value="Guest")
        if st.button("Continue as Guest"):
            st.session_state.user = f"guest_{guest_name}_{int(time.time())}"
            st.session_state.display_name = guest_name
            st.experimental_rerun()
    with col2:
        # Google login button (only works if secrets configured)
        google_link = google_oauth_start()
        if google_link:
            st.markdown(f"[Sign in with Google]({google_link}&auth=google){' '}")
            st.caption("Use Google to save chats across devices (requires Google OAuth in Streamlit Secrets).")
        else:
            st.info("Google Login not configured. Add GOOGLE_CLIENT_ID and REDIRECT_URI to Streamlit Secrets to enable.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# user is present
username = st.session_state.user
display_name = st.session_state.get("display_name", username)

# load persisted chats into session_state if not loaded
if "chats_loaded_for" not in st.session_state or st.session_state.chats_loaded_for != username:
    st.session_state.chat_history = load_chats(username)
    st.session_state.chats_loaded_for = username

# ----------------- CLEAN AI CALL with retries + safe parsing -----------------
def ask_openai(prompt, model="gpt-4o-mini", temp=0.45, max_retries=2):
    key = st.secrets.get("OPENAI_API_KEY")
    if not key:
        return "❌ No OPENAI_API_KEY found in Streamlit Secrets. Add it and redeploy."

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are StudyGenie, a friendly concise study assistant."},
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
            time.sleep(1.2)
            continue

        try:
            rj = r.json()
        except Exception as e:
            if attempt > max_retries:
                return f"❌ Invalid JSON from AI: {e}"
            time.sleep(0.8)
            continue

        # handle API error
        if "error" in rj:
            # if rate limit or server error, retry a couple times
            err_msg = rj["error"].get("message", str(rj["error"]))
            if attempt <= max_retries and ("rate limit" in err_msg.lower() or r.status_code >= 500):
                time.sleep(1.5)
                continue
            return f"❌ AI error: {err_msg}"

        # safe extraction
        choices = rj.get("choices")
        if not choices:
            if attempt <= max_retries:
                time.sleep(0.8)
                continue
            return "❌ AI returned no choices. Try again in a moment."

        # extract content robustly
        msg = choices[0].get("message") or choices[0].get("text") or {}
        content = ""
        if isinstance(msg, dict):
            content = msg.get("content") or msg.get("text") or ""
        else:
            content = str(msg)

        if not content and attempt <= max_retries:
            time.sleep(0.6)
            continue

        # success
        return content or "❌ Empty response from AI."
    return "❌ Failed after retries."

# ----------------- LAYOUT -----------------
st.markdown("<div class='wide'>", unsafe_allow_html=True)
c1, c2 = st.columns([4,1])
with c1:
    st.markdown(f"**Signed in as:** {display_name}")
with c2:
    if st.button("Logout"):
        # persist chats
        save_chats(username, st.session_state.chat_history)
        for k in ["user", "display_name", "chats_loaded_for"]:
            if k in st.session_state: del st.session_state[k]
        st.experimental_rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ----------------- NAV (quick jump 1-5) -----------------
col1, col2, col3, col4, col5 = st.columns(5)
if col1.button("1️⃣ Doubt"): page = "Doubt"
elif col2.button("2️⃣ Flashcards"): page = "Flashcards"
elif col3.button("3️⃣ Notes"): page = "Notes"
elif col4.button("4️⃣ Planner"): page = "Planner"
elif col5.button("5️⃣ Boost"): page = "Boost"
else:
    # default page from sidebar selection
    sidebar_choice = st.sidebar.selectbox("Go to", ["Doubt","Flashcards","Notes","Summary","AnswerChecker","Planner","Voice","Saved","Profile","Boost"])
    page = sidebar_choice

# ----------------- PAGE: Doubt Solver -----------------
if page == "Doubt":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💡 AI Doubt Solver")
    q = st.text_area("Ask your question:", key="doubt_in")
    if st.button("Solve"):
        if q.strip():
            with st.spinner("Thinking..."):
                ans = ask_openai(q)
            # append to history and save
            st.session_state.chat_history.append({"role":"user","text":q,"time":int(time.time())})
            st.session_state.chat_history.append({"role":"ai","text":ans,"time":int(time.time())})
            save_chats(username, st.session_state.chat_history)
            st.markdown("**Answer:**")
            st.write(ans)
        else:
            st.warning("Ask something first!")
    # show recent chat
    if st.checkbox("Show chat history"):
        for msg in reversed(st.session_state.chat_history[-30:]):
            cls = "chat-user" if msg["role"]=="user" else "chat-ai"
            st.markdown(f"<div class='{cls}'>{msg['text']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: Flashcards (generate & SRS placeholder) -----------------
elif page == "Flashcards":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🃏 Flashcards")
    topic = st.text_input("Topic for flashcards:")
    count = st.slider("How many cards?", 3, 20, 6)
    if st.button("Generate Cards"):
        if topic.strip():
            raw = ask_openai(f"Create {count} simple Q & A flashcards for: {topic}. Use 'Q:' and 'A:' labels.")
            # basic parse
            cards=[]
            for line in raw.splitlines():
                line=line.strip()
                if line.lower().startswith("q:"):
                    qline=line.split(":",1)[1].strip()
                    cards.append({"q":qline,"a":""})
                elif line.lower().startswith("a:") and cards:
                    cards[-1]["a"]=line.split(":",1)[1].strip()
            if not cards:
                # fallback split paragraphs
                parts=[p.strip() for p in raw.split("\n\n") if p.strip()]
                for p in parts:
                    if ":" in p:
                        k,v=p.split(":",1)
                        cards.append({"q":k.strip()[:200],"a":v.strip()})
            st.session_state.flashcards = cards
            st.success(f"Created {len(cards)} cards.")
        else:
            st.warning("Enter a topic.")
    if st.session_state.get("flashcards"):
        idx = st.number_input("Card index", 1, max(1,len(st.session_state.flashcards)), 1)
        card = st.session_state.flashcards[idx-1]
        st.markdown(f"**Q:** {card['q']}")
        if st.button("Show Answer"):
            st.markdown(f"**A:** {card['a']}")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: Notes (generate & save) -----------------
elif page == "Notes":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 Notes Generator")
    notes_topic = st.text_input("Topic:")
    if st.button("Generate Notes"):
        if notes_topic.strip():
            out = ask_openai(f"Create concise class notes for: {notes_topic}. Use bullets and short examples.")
            st.text_area("Generated notes", value=out, height=260, key="gen_notes_box")
        else:
            st.warning("Enter a topic.")
    if st.session_state.get("gen_notes_box"):
        if st.button("Save Notes"):
            st.session_state.notes_store.append({"title": notes_topic or "Untitled", "content": st.session_state.get("gen_notes_box")})
            save_chats(username, st.session_state.chat_history)  # save chat too just to persist
            st.success("Saved.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: Summary (Brain-dump cleaner) -----------------
elif page == "Summary":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🧠 Brain-dump Cleaner")
    messy = st.text_area("Paste messy notes / ideas here:")
    if st.button("Clean"):
        if messy.strip():
            out = ask_openai(f"Organize and clean this brain-dump into titled sections and action items:\n{messy}")
            st.write(out)
            # store in chat history as action
            st.session_state.chat_history.append({"role":"user","text":"Brain-dump cleaned","time":int(time.time())})
            st.session_state.chat_history.append({"role":"ai","text":out,"time":int(time.time())})
            save_chats(username, st.session_state.chat_history)
        else:
            st.warning("Paste something.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: Answer Checker -----------------
elif page == "AnswerChecker":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("✅ Answer Checker")
    q = st.text_input("Question:")
    stud = st.text_area("Student's answer:")
    if st.button("Check"):
        if q.strip() and stud.strip():
            out = ask_openai(f"Question: {q}\nStudent Answer: {stud}\nGive a score /10 and concise feedback with corrections.")
            st.write(out)
            st.session_state.chat_history.append({"role":"user","text":f"Checked answer for: {q}","time":int(time.time())})
            st.session_state.chat_history.append({"role":"ai","text":out,"time":int(time.time())})
            save_chats(username, st.session_state.chat_history)
        else:
            st.warning("Add both fields.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: Planner -----------------
elif page == "Planner":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📆 Planner")
    task = st.text_input("New task:")
    deadline = st.text_input("Deadline (optional):")
    if st.button("Add task"):
        if task.strip():
            st.session_state.planner.append({"task":task,"deadline":deadline})
            st.success("Added.")
        else:
            st.warning("Enter a task.")
    if st.session_state.planner:
        for i,t in enumerate(st.session_state.planner,1):
            st.write(f"{i}. {t['task']} — {t['deadline']}")
        if st.button("Generate 7-day plan"):
            prompt = "Create a 7-day study schedule from these tasks:\n" + "\n".join([p["task"] for p in st.session_state.planner])
            out = ask_openai(prompt)
            st.write(out)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: Voice input (upload -> transcribe) -----------------
elif page == "Voice":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🎤 Voice Input (upload & transcribe)")
    audio = st.file_uploader("Upload audio (mp3/m4a/wav)", type=["mp3","m4a","wav"])
    if audio and st.button("Transcribe & Answer"):
        key = st.secrets.get("OPENAI_API_KEY")
        if not key:
            st.error("Add OPENAI_API_KEY to secrets.")
        else:
            files = {"file": (audio.name, audio.getvalue())}
            data = {"model":"gpt-4o-transcribe"}  # might need adjustment per your OpenAI access
            headers = {"Authorization": f"Bearer {key}"}
            try:
                r = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=90)
                rj = r.json()
                if "error" in rj:
                    st.error("Transcription error: " + str(rj["error"].get("message","")))
                else:
                    text = rj.get("text","")
                    st.write("Transcribed Text:")
                    st.write(text)
                    out = ask_openai("Answer based on the transcription:\n" + text)
                    st.write("AI Answer:")
                    st.write(out)
            except Exception as e:
                st.error("Transcription failed: " + str(e))
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: Saved (notes & chats) -----------------
elif page == "Saved":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💾 Saved Notes & Chats")
    # saved notes
    if st.session_state.notes_store:
        for i,n in enumerate(st.session_state.notes_store,1):
            with st.expander(n["title"]):
                st.write(n["content"])
                st.download_button(f"Download {n['title']}", n["content"], file_name=f"{n['title']}.txt")
    else:
        st.info("No saved notes.")
    # saved chats preview & download
    if st.session_state.chat_history:
        st.write("Recent chat entries (latest first):")
        for msg in st.session_state.chat_history[-20:][::-1]:
            who = "You" if msg["role"]=="user" else "StudyGenie"
            st.write(f"**{who}:** {msg['text']}")
        if st.button("Download chat history"):
            fname = f"chats_{username}.json"
            st.download_button("Download JSON", json.dumps(st.session_state.chat_history, ensure_ascii=False, indent=2), file_name=fname)
    else:
        st.info("No chats yet.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: Profile -----------------
elif page == "Profile":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👤 Profile")
    n = st.text_input("Display name", value=st.session_state.get("display_name",""))
    g = st.text_input("Grade / Year", value=st.session_state.profile.get("grade",""))
    goal = st.text_input("Short goal", value=st.session_state.profile.get("goal",""))
    if st.button("Save profile"):
        st.session_state.display_name = n or st.session_state.display_name
        st.session_state.profile.update({"grade":g,"goal":goal,"name":st.session_state.display_name})
        st.success("Profile saved.")
    st.write(st.session_state.profile)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: Boost (Motivation) -----------------
elif page == "Boost":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💖 Motivation Booster")
    mega = [
        "Bestie you're UNSTOPPABLE 🔥","Your future self is so proud 💗","Focus now → flex later ✨",
        "Small steps = massive glow-up","Korean apartment vibes loading…","Discipline looks cute on you"
    ]
    if st.button("Boost me"):
        st.success(random.choice(mega))
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- ensure chats saved on exit-ish -----------------
save_chats(username, st.session_state.chat_history)

# ----------------- footer -----------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; font-size:12px; color:rgba(0,0,0,0.55)'>StudyGenie Pro — made with ❤️. Use OpenAI key in Streamlit Secrets.</div>", unsafe_allow_html=True)