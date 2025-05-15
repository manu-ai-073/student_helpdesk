import streamlit as st
import requests
import json

# Page config
st.set_page_config(page_title="📚 Student Helper Chatbot", layout="centered")

# Title
st.title("📚 Student Helper Chatbot")
st.markdown("""
This chatbot helps you with:
- 🧠 Summarizing text
- 🧮 Solving math expressions or equations
- 📝 Generating quizzes from your input
""")

# Feature selector
feature = st.selectbox("Select a feature:", ["Summarizer", "Math Solver", "Quiz Generator"])

# Input area for Summarizer and Math Solver
if feature in ["Summarizer", "Math Solver"]:
    user_input = st.text_area("✍️ Enter your text or equation here:")

# Input area for Quiz Generator
if feature == "Quiz Generator":
    quiz_topic = st.text_input("Enter quiz topic:")
    num_questions = st.number_input("How many questions to generate?", min_value=1, max_value=10, value=3)

if st.button("🔍 Run"):
    if feature == "Summarizer":
        if not user_input.strip():
            st.warning("Please enter some text to summarize.")
        else:
            try:
                headers = {
                    "Authorization": f"Bearer {st.secrets['HF_TOKEN']}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "inputs": user_input
                }
                response = requests.post(
                    "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
                    headers=headers, json=payload
                )
                result = response.json()
                if isinstance(result, dict) and 'error' in result:
                    st.error("❌ Error while summarizing: " + result['error'])
                else:
                    st.success("✅ Summary:")
                    st.write(result[0]['summary_text'])
            except Exception as e:
                st.error(f"❌ Exception: {e}")

    elif feature == "Math Solver":
        if not user_input.strip():
            st.warning("Please enter a math problem.")
        else:
            try:
                math_prompt = f"Solve the following math problem step by step: {user_input}"
                headers = {
                    "Authorization": f"Bearer {st.secrets['HF_TOKEN']}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "inputs": math_prompt
                }
                response = requests.post(
                    "https://api-inference.huggingface.co/models/google/flan-t5-xl",
                    headers=headers, json=payload
                )
                result = response.json()
                if isinstance(result, dict) and 'error' in result:
                    st.error("❌ Error: " + result['error'])
                else:
                    st.success("✅ Solution:")
                    st.write(result[0]['generated_text'])
            except Exception as e:
                st.error(f"❌ Exception: {e}")

    elif feature == "Quiz Generator":
        if not quiz_topic.strip():
            st.warning("Please enter a topic for the quiz.")
        else:
            try:
                headers = {
                    "Authorization": f"Bearer {st.secrets['HF_TOKEN']}",
                    "Content-Type": "application/json"
                }
                prompt = f"""Generate {num_questions} multiple-choice questions (MCQs) with 4 options and answers on the topic "{quiz_topic}". 
    Each question should be clearly numbered and provide the correct answer after the options."""
                payload = {
                    "inputs": prompt
                }
                response = requests.post(
                    "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
                    headers=headers, json=payload
                )
                result = response.json()
                if isinstance(result, dict) and 'error' in result:
                    st.error("❌ Error while generating quiz: " + result['error'])
                elif isinstance(result, list):
                    st.success("🎯 Quiz Generator Result")
                    st.write(result[0].get('generated_text', '⚠️ No quiz generated.'))
                else:
                    st.error("❌ Unexpected response format from model.")
            except Exception as e:
                st.error(f"❌ Exception: {e}")
