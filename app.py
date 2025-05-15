import streamlit as st
import requests
import sympy
from sympy import symbols, Eq, solve

# Load Hugging Face Token securely
API_TOKEN = st.secrets["HF_TOKEN"]
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Hugging Face models
SUMMARIZER_MODEL = "facebook/bart-large-cnn"
QUIZ_MODEL = "tuner007/t5_paraphrase_paws"

# App layout
st.set_page_config(page_title="🎓 Student Helper", layout="centered")
st.title("🎓 Student Helper Chatbot")
st.markdown("An all-in-one tool to help students with summarizing, math solving, and quiz creation.")

# Feature selection UI
col1, col2, col3 = st.columns(3)
with col1:
    summarize_mode = st.button("📄 Summarizer")
with col2:
    math_mode = st.button("🧮 Math Solver")
with col3:
    quiz_mode = st.button("❓ Quiz Generator")

# Text input area
user_input = st.text_area("✍️ Enter your text or equation here:")

# Summarizer
def summarize_text(text):
    url = f"https://api-inference.huggingface.co/models/{SUMMARIZER_MODEL}"
    payload = {"inputs": text}
    res = requests.post(url, headers=headers, json=payload)
    try:
        result = res.json()
        if isinstance(result, list):
            return "✅ Summary:\n\n" + result[0]["summary_text"]
        elif "error" in result:
            return f"⚠️ {result['error']}"
    except:
        return "❌ Error while summarizing."

# Math Solver
def solve_equation(expr):
    try:
        x = symbols("x")
        if "=" in expr:
            lhs, rhs = map(sympy.sympify, expr.split("="))
            eq = Eq(lhs, rhs)
            sol = solve(eq, x)
            return f"✅ Solution: x = {sol}"
        else:
            res = sympy.sympify(expr)
            return f"✅ Result: {res}"
    except Exception as e:
        return "❌ Error: Invalid math expression."

# Quiz Generator
def generate_quiz(text):
    url = f"https://api-inference.huggingface.co/models/{QUIZ_MODEL}"
    payload = {"inputs": f"Create a question from: {text}"}
    res = requests.post(url, headers=headers, json=payload)
    try:
        result = res.json()
        if isinstance(result, list):
            return "✅ Quiz Question:\n\n" + result[0]["generated_text"]
        elif "error" in result:
            return f"⚠️ {result['error']}"
    except:
        return "❌ Error while generating quiz."

# Response Logic
if user_input:
    if summarize_mode:
        st.markdown("### 🧠 Summarizer Result")
        st.write(summarize_text(user_input))
    elif math_mode:
        st.markdown("### 🔢 Math Solver Result")
        st.write(solve_equation(user_input))
    elif quiz_mode:
        st.markdown("### 🎯 Quiz Generator Result")
        st.write(generate_quiz(user_input))
else:
    st.info("Enter your input above and choose a feature to proceed.")
