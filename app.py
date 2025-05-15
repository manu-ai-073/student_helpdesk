import streamlit as st
import openai
import sympy as sp
import os

# 🔐 Set your OpenAI API key here or use an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY") or "your-openai-api-key"

# 📌 Streamlit UI setup
st.set_page_config(page_title="Student Helper Chatbot", layout="centered")
st.title("🎓 Student Helper Chatbot")

# Sidebar for feature selection
feature = st.sidebar.selectbox("Choose a feature:", ["Quiz Generator", "Math Solver", "Summarizer"])

def ask_gpt(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful educational assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {e}"

# 📋 Quiz Generator
if feature == "Quiz Generator":
    st.header("📋 Quiz Generator")
    topic = st.text_input("Enter a topic or subject (e.g., Class 10 Science):")
    num_questions = st.slider("Number of questions", 1, 10, 5)
    if st.button("Generate Quiz") and topic:
        prompt = f"Generate {num_questions} multiple-choice questions on the topic '{topic}'. Each question should have 4 options and indicate the correct answer."
        result = ask_gpt(prompt)
        st.markdown(result)

# 🔢 Math Solver
elif feature == "Math Solver":
    st.header("🔢 Math Solver")
    problem = st.text_input("Enter a math expression or equation:")
    if st.button("Solve") and problem:
        try:
            expr = sp.sympify(problem)
            solution = sp.solve(expr)
            st.write(f"🧮 SymPy Solution: {solution}")
        except:
            # Use GPT if SymPy can't solve it
            prompt = f"Solve this math problem step-by-step: {problem}"
            result = ask_gpt(prompt)
            st.markdown(result)

# 📝 Summarizer
elif feature == "Summarizer":
    st.header("📝 Text Summarizer")
    text = st.text_area("Paste the text you want to summarize:")
    summary_length = st.radio("Choose summary type:", ["Short", "Bullet Points", "Detailed"])
    if st.button("Summarize") and text:
        if summary_length == "Short":
            prompt = f"Summarize this in 1-2 lines: {text}"
        elif summary_length == "Bullet Points":
            prompt = f"Summarize this in bullet points: {text}"
        else:
            prompt = f"Give a detailed summary of the following text: {text}"
        result = ask_gpt(prompt)
        st.markdown(result)
