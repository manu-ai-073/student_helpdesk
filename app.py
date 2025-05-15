import streamlit as st
import requests
import sympy
from sympy import symbols, Eq, solve
from requests.exceptions import RequestException

# Load Hugging Face Token from secrets
API_TOKEN = st.secrets["HF_TOKEN"]
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Hugging Face Models
SUMMARIZER_MODEL = "Falconsai/text_summarization"
QUIZ_MODEL = "tuner007/t5_paraphrase_paws"

# --- Helper Functions ---
def summarize_text(text):
    url = f"https://api-inference.huggingface.co/models/{SUMMARIZER_MODEL}"
    payload = {"inputs": text}
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        result = res.json()
        if isinstance(result, list) and 'summary_text' in result[0]:
            return result[0]['summary_text']
        elif "error" in result:
            return f"⏳ {result['error']}"
    except RequestException as e:
        return f"❌ Request error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected summarizer error: {str(e)}"

def generate_quiz(text):
    url = f"https://api-inference.huggingface.co/models/{QUIZ_MODEL}"
    payload = {"inputs": f"Create a question from: {text}"}
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        result = res.json()
        if isinstance(result, list) and 'generated_text' in result[0]:
            return result[0]['generated_text']
        elif "error" in result:
            return f"⏳ {result['error']}"
    except RequestException as e:
        return f"❌ Request error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected quiz generation error: {str(e)}"

def solve_equation(expr):
    try:
        if "=" in expr:
            lhs, rhs = map(sympy.sympify, expr.split("="))
            variables = list(lhs.free_symbols.union(rhs.free_symbols))
            equation = Eq(lhs, rhs)
            solution = solve(equation, variables)
            return f"Solution: {solution}"
        else:
            result = sympy.sympify(expr)
            return f"Result = {result}"
    except Exception as e:
        return f"❌ Invalid math expression: {str(e)}"

# --- Streamlit UI ---
st.set_page_config(page_title="🎓 Student Helper", layout="centered")
st.title("🎓 Student Helper Chatbot")

feature = st.selectbox("Select a Feature", ["Summarizer", "Math Solver", "Quiz Generator"])
user_input = st.text_area("Enter your text or expression:")

if st.button("Get Result"):
    if not user_input.strip():
        st.warning("Please enter something!")
    else:
        with st.spinner("Processing..."):
            if feature == "Summarizer":
                st.write(summarize_text(user_input))
            elif feature == "Math Solver":
                st.write(solve_equation(user_input))
            elif feature == "Quiz Generator":
                st.write(generate_quiz(user_input))

# Option to download result - optional future enhancement
# if result:
#     st.download_button("Download Result", result, file_name="output.txt")
