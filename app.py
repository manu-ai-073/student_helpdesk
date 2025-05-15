import streamlit as st
import requests
import sympy
from sympy import simplify

# Load Hugging Face API key from secrets.toml
API_TOKEN = st.secrets["HF_TOKEN"]
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Hugging Face endpoints
SUMMARIZER_MODEL = "facebook/bart-large-cnn"
QUIZ_MODEL = "tuner007/t5_paraphrase_paws"

# Streamlit UI
st.set_page_config(page_title="🎓 Student Helper Chatbot", layout="centered")
st.title("🎓 Student Helper Chatbot")

# Feature Selection
feature = st.selectbox("Select a feature:", ["Summarizer", "Math Solver", "Quiz Generator"])
user_input = st.text_area("Enter your text or math expression here:")

def summarize_text(text):
    url = f"https://api-inference.huggingface.co/models/{SUMMARIZER_MODEL}"
    payload = {"inputs": text}
    res = requests.post(url, headers=headers, json=payload)
    return res.json()[0]['summary_text']

def generate_quiz(text):
    url = f"https://api-inference.huggingface.co/models/{QUIZ_MODEL}"
    payload = {"inputs": f"Generate a quiz question from: {text}"}
    res = requests.post(url, headers=headers, json=payload)
    return res.json()[0]['generated_text']

def solve_math(expression):
    try:
        result = simplify(sympy.sympify(expression))
        return str(result)
    except Exception as e:
        return "❌ Error: Invalid math expression."

if st.button("Get Result"):
    if not user_input.strip():
        st.warning("⚠️ Please enter input text.")
    else:
        if feature == "Summarizer":
            with st.spinner("Summarizing..."):
                try:
                    summary = summarize_text(user_input)
                    st.success("✅ Summary:")
                    st.write(summary)
                except Exception as e:
                    st.error("❌ Error while summarizing.")
        elif feature == "Math Solver":
            with st.spinner("Solving..."):
                result = solve_math(user_input)
                st.success("✅ Solution:")
                st.write(result)
        elif feature == "Quiz Generator":
            with st.spinner("Generating quiz..."):
                try:
                    quiz = generate_quiz(user_input)
                    st.success("✅ Quiz Question:")
                    st.write(quiz)
                except Exception as e:
                    st.error("❌ Error while generating quiz.")
