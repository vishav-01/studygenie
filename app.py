def ask_ai(prompt):
    import requests, json, time

    api_key = st.secrets.get("OPENAI_API_KEY", "")

    if not api_key:
        return "❌ Bestie, no API key found in Streamlit Secrets."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "You are StudyGenie, a friendly, cute, supportive study bestie."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 350,
        "temperature": 0.65
    }

    try:
        req = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,  # using json= instead of data= fixes many issues
            timeout=25
        )

        result = req.json()

        # Handle errors gracefully
        if "error" in result:
            err = result["error"]["message"]

            # Quota error
            if "quota" in err.lower():
                return "🥺 Bestie you ran out of AI quota. Recharge your OpenAI balance."

            # Other AI errors
            return f"⚠️ AI Error: {err}"

        # If no choices returned
        if "choices" not in result:
            return "⚠️ Bestie, the AI glitched for a moment. Try again."

        reply = result["choices"][0]["message"]["content"]

        # Save chat history safely
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        st.session_state.chat_history.append({"you": prompt, "ai": reply})

        return reply

    except requests.exceptions.Timeout:
        return "⏳ Bestie, the AI took too long. Try again."

    except Exception as e:
        return "❌ Error: " + str(e)