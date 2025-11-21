import streamlit as st
from agents import DataScienceAgent

st.title("🧠 StudyGenie Agent Mode")

base_url = st.text_input("Base URL (LLM endpoint)", "https://api.openai.com/v1")
model = st.text_input("Model Name", "gpt-4o-mini")

user_input = st.text_area("Ask anything:")

if st.button("Run Agent"):
    agent = DataScienceAgent(base_url=base_url, model=model)
    agent.add_system_message("You are a helpful AI agent.")
    agent.add_user_message(user_input)
    answer = agent.run()
    st.write(answer)