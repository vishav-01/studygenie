# app.py (diagnostic)
import streamlit as st
import importlib
import sys
import traceback

st.set_page_config(page_title="StudyGenie Debug", layout="centered")
st.title("StudyGenie — Debug Mode 🔎")

# 1) Show whether secret exists (we DO NOT print the secret)
has_secret = "OPENAI_API_KEY" in st.secrets
st.write("OPENAI_API_KEY present in Secrets:", has_secret)

# 2) Show installed openai package version (if any)
try:
    import openai
    st.write("openai module version:", openai.__version__)
except Exception as e:
    st.write("openai module not installed or import failed:", str(e))

# 3) Show python version
st.write("Python version:", sys.version.splitlines()[0])

# 4) Quick test: try 2 different client patterns (new SDK and old top-level). 
st.markdown("---")
st.header("Test API call")

if not has_secret:
    st.warning("Add OPENAI_API_KEY to Streamlit Secrets (Settings → Secrets) and redeploy.")
else:
    st.info("Trying to call the API. Please wait (may take a few seconds).")

    # attempt 1: new SDK pattern
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        st.write("Using `from openai import OpenAI` pattern — attempting responses.create...")
        try:
            resp = client.responses.create(model="gpt-4o-mini", input="Say hi in 5 words.")
            # try to safely extract text
            text = None
            try:
                text = resp.output[0].content[0].text
            except Exception:
                # fallback: stringify
                text = str(resp)
            st.success("New SDK call succeeded. Response preview:")
            st.write(text)
        except Exception as e:
            st.error("New SDK call FAILED. See stacktrace below.")
            st.text(traceback.format_exc())
    except Exception as e:
        st.write("New SDK import pattern failed:", str(e))
        st.text(traceback.format_exc())

    st.markdown("---")

    # attempt 2: classic openai top-level client (older pattern)
    try:
        import openai as oai
        oai.api_key = st.secrets["OPENAI_API_KEY"]
        st.write("Using `import openai` pattern — attempting ChatCompletion.create...")
        try:
            resp2 = oai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content":"Summarize 'photosynthesis' in one line."}],
                max_tokens=60
            )
            text2 = resp2["choices"][0]["message"]["content"]
            st.success("Old-style ChatCompletion succeeded. Preview:")
            st.write(text2)
        except Exception as e:
            st.error("Old-style ChatCompletion FAILED. See stacktrace below.")
            st.text(traceback.format_exc())
    except Exception as e:
        st.write("Old openai import failed:", str(e))
        st.text(traceback.format_exc())

st.markdown("---")
st.write("After you see which pattern works, I will give you the final production code. If both fail, paste the logs here or screenshot them and I will debug further.")