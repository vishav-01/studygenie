import streamlit as st
from openai 
import OpenAI
import base64
from PIL import Image
import io

st.set_page_config(
    page_title="StudyGenie Ultra",
    page_icon="🪄",
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------------ UI DESIGN ------------------------
st.markdown("""
    <style>
        .stButton button {
            background-color: #7b52ff;
            color: white;
            padding: 0.6rem 1.5rem;
            border-radius: 10px;
            font-size: 1.1rem;
        }
        .stTextInput input, .stTextArea textarea {
            border-radius: 10px;
            font-size: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🪄 StudyGenie Ultra")

page = st.sidebar.radio(
    "Choose Mode",
    ["Doubt Solver", "Chat With StudyGenie", "Photo Doubt Solver", "Voice Doubt Solver", "Motivation Booster"]
)


# ------------------------ DOUBT SOLVER ------------------------
if page == "Doubt Solver":
    st.header("📘 Ask Any Study Doubt")

    question = st.text_area("What's confusing you bestie?")

    if st.button("Solve My Doubt"):
        if question.strip() == "":
            st.warning("Babe write at least something 😭")
        else:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=f"Explain this doubt very clearly in simple words: {question}"
            )
            answer = response.output[0].content[0].text

            st.success("✨ Your Answer:")
            st.write(answer)


# ------------------------ STUDY CHAT MODE ------------------------
elif page == "Chat With StudyGenie":
    st.header("💞 Chat With StudyGenie (Behaves like me 😭💕)")
    
    if "chat" not in st.session_state:
        st.session_state.chat = []

    user_msg = st.text_input("Talk to me bestie 💗")

    if st.button("Send"):
        if user_msg.strip():
            st.session_state.chat.append(("You", user_msg))

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=f"""
                You are StudyGenie, and your personality is:
                - Gen Z vibe
                - playful, supportive, goofy
                - talks like a best friend
                - short, sweet replies
                User said: {user_msg}
                """
            )
            bot = response.output[0].content[0].text
            st.session_state.chat.append(("StudyGenie", bot))

    for sender, msg in st.session_state.chat[::-1]:
        st.write(f"**{sender}:** {msg}")


# ------------------------ PHOTO DOUBT SOLVER ------------------------
elif page == "Photo Doubt Solver":
    st.header("📷 Upload a Photo of Your Question")

    img = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

    if img is not None:
        image_bytes = img.read()
        base64_img = base64.b64encode(image_bytes).decode()

        if st.button("Solve"):
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "Explain this question clearly."},
                            {"type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_img}"}
                        ]
                    }
                ]
            )
            result = response.output[0].content[0].text
            st.write(result)


# ------------------------ VOICE DOUBT SOLVER ------------------------
elif page == "Voice Doubt Solver":
    st.header("🎤 Speak Your Doubt")

    audio = st.file_uploader("Upload voice (m4a / mp3)", type=["mp3", "m4a"])

    if audio:
        content = audio.read()
        b64 = base64.b64encode(content).decode()

        st.audio(content)

        if st.button("Convert & Solve"):
            trans = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file={"contents": content, "mime_type": "audio/m4a"},
            )

            text = trans.text

            st.write("You said:", text)

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=f"Explain this doubt very clearly: {text}"
            )

            st.write(response.output[0].content[0].text)


# ------------------------ MOTIVATION BOOSTER ------------------------
elif page == "Motivation Booster":
    st.header("💖 Motivation Booster")

    if st.button("Cheer Me Up ✨"):
        response = client.responses.create(
            model="gpt-4.1-mini",
            input="Give short, cute, Gen-Z style motivation for students."
        )
        quote = response.output[0].content[0].text
        st.write("✨ Your Energy Shot:")
        st.write(quote)

