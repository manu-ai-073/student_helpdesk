import streamlit as st
import sympy
from sympy import symbols, Eq, solve
import requests

# ------------------ CONFIG ------------------
st.set_page_config(page_title="📚 Student Helper Chatbot", layout="centered")
st.title("🤖 Student Helper Chatbot")
st.markdown("""
This chatbot helps you with:
- 🧠 Summarizing text
- 🧮 Solving math expressions or equations
- 📝 Generating quizzes from your input
""")

# ------------------ INPUT ------------------
st.sidebar.title("🔧 Features")
feature = st.sidebar.radio("Select a feature:", ["Math Solver", "Summarizer", "Quiz Generator"])

input_text = st.text_area("✍️ Enter your text or equation here:")

# ------------------ Math Solver ------------------
def solve_equation(expr):
    try:
        x = symbols("x")  # define the variable
        if "=" in expr:
            lhs, rhs = expr.split("=")
            lhs = sympy.sympify(lhs.strip())
            rhs = sympy.sympify(rhs.strip())
            eq = Eq(lhs, rhs)
            sol = solve(eq, x)
            return f"✅ Solution: x = {sol[0]}" if sol else "❌ No solution found."
        else:
            res = sympy.sympify(expr)
            return f"✅ Result: {res}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ------------------ Summarizer ------------------
def summarize_text(text):
    try:
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        payload = {"inputs": text}
        response = requests.post(API_URL, headers=headers, json=payload)
        summary = response.json()
        if isinstance(summary, list):
            return f"✅ Summary: {summary[0]['summary_text']}"
        else:
            return f"❌ Error while summarizing."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ------------------ Quiz Generator ------------------
def generate_quiz(text):
    try:
        API_URL = "https://api-inference.huggingface.co/models/tuner007/t5_paraphrase_paws"
        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        payload = {"inputs": f"paraphrase: {text} </s>", "parameters": {"num_return_sequences": 1}}
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        if isinstance(result, list):
            return f"✅ Quiz Question: {result[0]['generated_text']}"
        else:
            return f"❌ Error while generating quiz."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ------------------ Output Area ------------------
if st.button("🔍 Submit"):
    if not input_text.strip():
        st.warning("Please enter some input.")
    else:
        if feature == "Math Solver":
            result = solve_equation(input_text)
            st.subheader("🧮 Math Solver Result")
            st.write(result)

        elif feature == "Summarizer":
            result = summarize_text(input_text)
            st.subheader("🧠 Summary")
            st.write(result)

        elif feature == "Quiz Generator":
            result = generate_quiz(input_text)
            st.subheader("🎯 Quiz Generator Result")
            st.write(result)

# ------------------ Footer ------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit and Hugging Face APIs")
