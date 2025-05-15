import streamlit as st
import google.generativeai as genai

# Set page config
st.set_page_config(page_title="Student Helper Chatbot", layout="centered")

# Configure Gemini API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize Gemini Pro model
model = genai.GenerativeModel("gemini-pro")

# Title
st.title("🎓 Student Helper Chatbot")

# Feature selection
feature = st.selectbox("Select a feature", ["Summarizer", "Math Solver", "Quiz Generator"])

# User input
user_input = st.text_area("Enter your input:")

# Generate response
if st.button("Get Help"):
    if user_input.strip() == "":
        st.warning("Please enter some input.")
    else:
        if feature == "Summarizer":
            prompt = f"Summarize this content:\n{user_input}"
        elif feature == "Math Solver":
            prompt = f"Solve this math problem step-by-step:\n{user_input}"
        elif feature == "Quiz Generator":
            prompt = f"Generate 5 quiz questions (with answers) from the following text:\n{user_input}"
        else:
            prompt = user_input

        try:
            response = model.generate_content(prompt)
            st.markdown("### 📘 Result:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {str(e)}")
