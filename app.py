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

# Input area
user_input = st.text_area("✍️ Enter your text or equation here:")

if feature == "Quiz Generator":
    num_questions = st.number_input("How many questions to generate?", min_value=1, max_value=10, value=3)

if st.button("🔍 Run"):
    if not user_input.strip():
        st.warning("Please enter some text or expression.")
    else:
        # --- Summarizer ---
        if feature == "Summarizer":
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

        # --- Math Solver using MathGPT API ---
        elif feature == "Math Solver":
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
                    "https://api-inference.huggingface.co/models/google/flan-t5-large",
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

        # --- Quiz Generator ---
        elif feature == "Quiz Generator":
            try:
                headers = {
                    "Authorization": f"Bearer {st.secrets['HF_TOKEN']}",
                    "Content-Type": "application/json"
                }
                prompt = f"Generate {num_questions} multiple-choice quiz questions with answers from the following topic: {user_input}"
                payload = {
                    "inputs": prompt
                }
                response = requests.post(
                    "https://api-inference.huggingface.co/models/google/flan-t5-large",
                    headers=headers, json=payload
                )
                result = response.json()
                if isinstance(result, dict) and 'error' in result:
                    st.error("❌ Error while generating quiz: " + result['error'])
                elif isinstance(result, list):
                    st.success("🎯 Quiz Generator Result")
                    st.write(result[0]['generated_text'])
                else:
                    st.error("❌ Unexpected response format from model.")
            except Exception as e:
                st.error(f"❌ Exception: {e}")
