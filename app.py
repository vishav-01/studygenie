import streamlit as st
from openai import OpenAI

# page setup
st.set_page_config(page_title="StudyGenie", page_icon="📚", layout="centered")

st.title("📚 StudyGenie — AI Study Helper")

# Input: API key
api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

# Input: your question
question = st.text_area("💬 Ask anything related to your studies:")

# Process
if st.button("✨ Generate Answer"):
    if not api_key:
        st.error("Please enter your API key!")
    elif not question:
        st.error("Please type a question!")
    else:
        try:
            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system",
                     "content": "You are StudyGenie — explain concepts in simple, easy, clear student-friendly language."
                    },
                    {"role": "user", "content": question}
                ]
            )

            generated_answer = response.choices[0].message.content

            st.subheader("✅ Your Answer:")
            st.write(generated_answer)

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")