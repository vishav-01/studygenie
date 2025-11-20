import streamlit as st
from openai import OpenAI

# Streamlit page settings
st.set_page_config(page_title="Study Genie", page_icon="📚")

# Title
st.title("📚 StudyGenie — Your Personal AI Study Buddy")

# Ask user for API key
api_key = st.text_input("Enter your OpenAI API Key:", type="password")

# Textbox
prompt = st.text_area("Ask your study question here:")

# Button
if st.button("Generate Answer"):
    if not api_key:
        st.error("Please enter your API key!")
    elif not prompt:
        st.error("Please enter a question!")
    else:
        try:
            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are StudyGenie, an AI that explains concepts in simple and clear language."},
                    {"role": "user", "content": prompt}
                ]
            )

            answer = response.choices[0].message.content
            st.success("✨ Answer Generated:")
            st.write(answer)

        except Exception as e:
            st.error(f"Error: {str(e)}")