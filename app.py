import streamlit as st
import requests
import sympy
from sympy import symbols, Eq, solve
import time

# Load Hugging Face Token from secrets
API_TOKEN = st.secrets["HF_TOKEN"]
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Streamlit UI
st.set_page_config(page_title="🎓 Student Helper", layout="wide")
st.title("🎓 Student Helper Chatbot")
st.markdown("---")

# Feature selector
feature = st.selectbox(
    "Select a Feature",
    ["Summarizer", "Math Solver", "Quiz Generator"],
    help="Choose the tool you want to use"
)

# Sidebar with feature descriptions
with st.sidebar:
    st.header("📚 Features Guide")
    st.markdown("""
    **Summarizer**: Condenses long text into key points using AI
    
    **Math Solver**: Solves equations and mathematical expressions
    
    **Quiz Generator**: Creates questions from your study material
    """)

# Hugging Face Models
SUMMARIZER_MODEL = "facebook/bart-large-xsum"  # Better summarization model
QUIZ_MODEL = "MingZhong/macaw-large"  # Dedicated question generation model

def query_huggingface(model_url, payload, max_retries=3, timeout=30):
    """Generic function to query Hugging Face with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.post(model_url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                return {"error": f"API Error: {str(e)}"}
            time.sleep(2 ** attempt)  # Exponential backoff
    return {"error": "Max retries reached"}

def summarize_text(text):
    url = f"https://api-inference.huggingface.co/models/{SUMMARIZER_MODEL}"
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": 150,
            "min_length": 40,
            "do_sample": False
        }
    }
    result = query_huggingface(url, payload)
    
    if isinstance(result, list):
        return result[0]['summary_text']
    elif isinstance(result, dict) and "error" in result:
        return f"⏳ {result['error']}"
    return "❌ Unexpected summarizer error."

def generate_quiz(text):
    url = f"https://api-inference.huggingface.co/models/{QUIZ_MODEL}"
    # Format prompt for better question generation
    prompt = f"Generate a multiple choice question based on this text: {text}"
    payload = {"inputs": prompt}
    
    result = query_huggingface(url, payload)
    
    if isinstance(result, list):
        return result[0]['generated_text']
    elif isinstance(result, dict) and "error" in result:
        return f"⏳ {result['error']}"
    return "❌ Unexpected quiz generation error."

def solve_equation(expr):
    try:
        # Handle multiple equations
        if ";" in expr:
            equations = expr.split(";")
            results = []
            for eq in equations:
                if "=" in eq:
                    lhs, rhs = map(sympy.sympify, eq.strip().split("="))
                    x = symbols("x")
                    equation = Eq(lhs, rhs)
                    sol = solve(equation, x)
                    results.append(f"x = {sol}")
                else:
                    result = sympy.sympify(eq.strip())
                    results.append(f"Result = {result}")
            return "\n".join(results)
        else:
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
        return f"❌ Invalid math expression: {str(e)}"

# Input area with contextual help
if feature == "Summarizer":
    user_input = st.text_area(
        "Enter the text to summarize:",
        height=200,
        help="Paste your text here. Works best with content between 100-1000 words."
    )
elif feature == "Math Solver":
    user_input = st.text_input(
        "Enter your mathematical expression:",
        help="Examples:\n2x + 3 = 7\n2 * (3 + 4)\nFor multiple equations, separate with semicolon"
    )
else:
    user_input = st.text_area(
        "Enter the text to generate questions from:",
        height=200,
        help="Enter a paragraph or concept you want to create questions about"
    )

if st.button("Get Result", type="primary"):
    if not user_input.strip():
        st.warning("Please enter something!")
    else:
        with st.spinner("Processing your request..."):
            if feature == "Summarizer":
                result = summarize_text(user_input)
                st.subheader("Summary")
                st.write(result)
                
            elif feature == "Math Solver":
                result = solve_equation(user_input)
                st.subheader("Solution")
                st.write(result)
                
            elif feature == "Quiz Generator":
                result = generate_quiz(user_input)
                st.subheader("Generated Question")
                st.write(result)
                
            # Show original text for reference
            with st.expander("Show Original Input"):
                st.write(user_input)
