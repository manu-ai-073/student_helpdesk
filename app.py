import streamlit as st
import requests

# Load secrets
HF_TOKEN = st.secrets.get("HF_TOKEN", "")
WOLFRAM_APP_ID = st.secrets.get("WOLFRAM_APP_ID", "")

# App Title and Description
st.set_page_config(page_title="📚 Student Helper Chatbot", layout="wide")
st.title("🤖 Student Helper Chatbot")
st.markdown("""
This chatbot helps you with:
- 🧠 Summarizing academic text
- 🧮 Solving math expressions or equations
- 📝 Generating quizzes from your input
""")

# Sidebar Navigation
feature = st.sidebar.radio("Choose a feature", ["📚 Summarizer", "🧮 Math Solver", "📝 Quiz Generator"])

# Universal Text Input
st.subheader(feature)
input_text = st.text_area("✍️ Enter your text or equation here:", height=200)

# Function: Summarizer using Cohere API
def summarize_with_cohere(text):
    try:
        url = "https://api.cohere.ai/v1/summarize"
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "length": "medium",
            "format": "paragraph",
            "model": "command",
            "extractiveness": "auto"
        }
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        return result.get("summary", "❌ Summarization failed.")
    except Exception as e:
        return f"❌ Error: {e}"

# Function: Math Solver using WolframAlpha API
def solve_math_mathjs(query):
    url = "http://api.mathjs.org/v4/"
    payload = {"expr": query}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.text
        else:
            return "❌ Could not solve the expression."
    except Exception as e:
        return f"❌ Error: {e}"


# Function: Quiz Generator using T5 Model from Hugging Face
def generate_quiz(text, num_questions=5):
    try:
        API_URL = "https://api-inference.huggingface.co/models/mrm8488/t5-base-finetuned-question-generation-ap"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        results = []
        for _ in range(num_questions):
            payload = {"inputs": f"generate questions: {text}"}
            response = requests.post(API_URL, headers=headers, json=payload)
            result = response.json()
            if isinstance(result, list):
                results.append(f"🔹 {result[0]['generated_text']}")
            else:
                results.append("⚠️ Failed to generate question.")
        return "\n".join(results)
    except Exception as e:
        return f"❌ Error: {e}"

# Run Feature on Submit
if st.button("🚀 Run") and input_text:
    if feature == "📚 Summarizer":
        st.subheader("🧠 Summary")
        st.success(summarize_with_cohere(input_text))

    elif feature == "🧮 Math Solver":
        st.subheader("✅ Solution")
        st.success(solve_math_wolfram(input_text))

    elif feature == "📝 Quiz Generator":
        st.subheader("🎯 Quiz Generator Result")
        num = st.slider("Select number of questions", 1, 10, 5)
        st.success(generate_quiz(input_text, num))
