import streamlit as st
import requests
import sympy
from sympy import symbols, Eq, solve

# Load Hugging Face Token from secrets
API_TOKEN = st.secrets["HF_TOKEN"]
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Streamlit UI
st.set_page_config(page_title="🎓 Student Helper", layout="centered")
st.title("🎓 Student Helper Chatbot")

# Feature selector
feature = st.selectbox("Select a Feature", ["Summarizer", "Math Solver", "Quiz Generator"])
user_input = st.text_area("Enter your text or expression:")

# Hugging Face Models
SUMMARIZER_MODEL = "facebook/bart-large-cnn"
QUIZ_MODEL = "tuner007/t5_paraphrase_paws"

def summarize_text(text):
    url = f"https://api-inference.huggingface.co/models/{SUMMARIZER_MODEL}"
    payload = {"inputs": text}
    res = requests.post(url, headers=headers, json=payload)

    try:
        result = res.json()
        if isinstance(result, list):
            return result[0]['summary_text']
        elif "error" in result:
            return f"⏳ {result['error']}"
    except:
        return "❌ Unexpected summarizer error."

def generate_quiz(text):
    url = f"https://api-inference.huggingface.co/models/{QUIZ_MODEL}"
    payload = {"inputs": f"Create a question from: {text}"}
    res = requests.post(url, headers=headers, json=payload)

    try:
        result = res.json()
        if isinstance(result, list):
            return result[0]['generated_text']
        elif "error" in result:
            return f"⏳ {result['error']}"
    except:
        return "❌ Unexpected quiz generation error."

def solve_equation(expr):
    try:
        if "=" in expr:
            lhs, rhs = map(sympy.sympify, expr.split("="))
            x = symbols("x")
            equation = Eq(lhs, rhs)
            sol = solve(equation, x)
            return f"x = {sol}"
        else:
            result = sympy.sympify(expr)
            return f"Result = {result}"
    except Exception as e:
        return "❌ Invalid math expression."

if st.button("Get Result"):
    if not user_input.strip():
        st.warning("Please enter something!")
    else:
        if feature == "Summarizer":
            st.info("Summarizing...")
            st.write(summarize_text(user_input))
        elif feature == "Math Solver":
            st.info("Solving math...")
            st.write(solve_equation(user_input))
        elif feature == "Quiz Generator":
            st.info("Generating quiz...")
            st.write(generate_quiz(user_input))
