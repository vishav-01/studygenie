import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="StudyGenie", page_icon="🪄")

# Load API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🪄 StudyGenie – Your AI Study Buddy")

# Navigation
page = st.sidebar.radio("Menu", ["Doubt Solver", "Motivation Booster"])

# ------------------ DOUBT SOLVER ------------------
if page == "Doubt Solver":
    st.header("📘 Ask Any Study Doubt")

    user_question = st.text_area("Type your question here:")

    if st.button("Solve My Doubt"):
        if user_question.strip() == "":
            st.warning("Please enter a question.")
        else:
            try:
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=f"You are StudyGenie, a friendly AI tutor. Answer this doubt simply and clearly:\n{user_question}"
                )

                answer = response.output[0].content[0].text
                st.success("✨ Here's your answer:")
                st.write(answer)

            except Exception as e:
                st.error(f"Error: {str(e)}")

# ------------------ MOTIVATION BOOSTER ------------------
elif page == "Motivation Booster":
    st.header("💖 Motivation Booster")

    if st.button("Give Me Motivation ✨"):
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input="Give short, positive, Gen-Z style motivation for students."
            )

            motivation = response.output[0].content[0].text
            st.write("🔥 Your Motivation:")
            st.write(motivation)

        except Exception as e:
            st.error(f"Error: {str(e)}")