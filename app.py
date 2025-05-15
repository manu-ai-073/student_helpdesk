import streamlit as st
import requests
import sympy
from sympy import symbols, Eq, solve
import time
import random
import json

# Configure page
st.set_page_config(
    page_title="🎓 Smart Study Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.github.com/yourusername/smart-study-assistant',
        'Report a bug': "https://www.github.com/yourusername/smart-study-assistant/issues",
        'About': "# Smart Study Assistant v2.0\nYour AI-powered study companion"
    }
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #cce5ff;
        border: 1px solid #b8daff;
        color: #004085;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
    .st-emotion-cache-16idsys p {
        font-size: 1.2em;
    }
</style>
""", unsafe_allow_html=True)

# Load Hugging Face Token from secrets
API_TOKEN = st.secrets["HF_TOKEN"]
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Updated Models configuration with more reliable models
MODELS = {
    "summarizer": "facebook/bart-large-cnn",  # Changed to BART for better summarization
    "quiz": "microsoft/DialoGPT-medium",      # Changed to DialoGPT for better question generation
    "qa": "deepset/roberta-base-squad2"       # Changed to RoBERTa for QA tasks
}

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/student-center.png", width=100)
    st.title("Smart Study Assistant")
    
    st.markdown("---")
    
    feature = st.radio(
        "Choose Your Tool",
        ["📝 Smart Summarizer", "🧮 Math Solver", "❓ Quiz Generator"],
        help="Select the tool you want to use"
    )
    
    st.markdown("---")
    
    # Feature-specific settings
    if feature == "📝 Smart Summarizer":
        st.markdown("### Summarizer Settings")
        summary_length = st.select_slider(
            "Summary Length",
            options=["Very Short", "Short", "Medium", "Long"],
            value="Medium"
        )
        style = st.select_slider(
            "Style",
            options=["Concise", "Detailed", "Academic"],
            value="Detailed"
        )
        
    elif feature == "❓ Quiz Generator":
        st.markdown("### Quiz Settings")
        question_type = st.multiselect(
            "Question Types",
            ["Multiple Choice", "True/False", "Short Answer"],
            default=["Multiple Choice"]
        )
        difficulty = st.select_slider(
            "Difficulty",
            options=["Easy", "Medium", "Hard"],
            value="Medium"
        )
        num_questions = st.slider("Number of Questions", 1, 10, 3)

def query_model(model_name, payload, max_retries=3):
    """Enhanced model query with better error handling and retry logic"""
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    
    for attempt in range(max_retries):
        try:
            with st.spinner(f"Processing (Attempt {attempt + 1}/{max_retries})..."):
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                st.error(f"Error: {str(e)}")
                return None
            time.sleep(2 ** attempt)
    return None

def generate_summary(text):
    """Enhanced summarization using BART model"""
    length_tokens = {
        "Very Short": 50,
        "Short": 100,
        "Medium": 150,
        "Long": 250
    }
    
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": length_tokens[summary_length],
            "min_length": length_tokens[summary_length] // 2,
            "do_sample": False
        }
    }
    
    result = query_model(MODELS["summarizer"], payload)
    if result and isinstance(result, list):
        return result[0]['summary_text']
    return "Error generating summary."

def generate_quiz_questions(text):
    """Enhanced quiz generation using DialoGPT"""
    questions = []
    
    question_templates = {
        "Multiple Choice": [
            "Generate a multiple choice question about: {}",
            "Create a quiz question with 4 options about: {}",
            "Make a multiple choice question based on: {}"
        ],
        "True/False": [
            "Create a true/false question about: {}",
            "Generate a true/false statement based on: {}"
        ],
        "Short Answer": [
            "Create a short answer question about: {}",
            "Generate a question that requires a brief explanation about: {}"
        ]
    }
    
    for _ in range(num_questions):
        for q_type in question_type:
            template = random.choice(question_templates[q_type])
            prompt = template.format(text)
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            result = query_model(MODELS["quiz"], payload)
            if result:
                # Process the response based on question type
                if isinstance(result, list) and result[0].get('generated_text'):
                    content = result[0]['generated_text']
                    questions.append({
                        "type": q_type.lower().replace(" ", "_"),
                        "content": content
                    })
    
    return questions

def solve_math(expr):
    """Enhanced math solver with step-by-step solutions"""
    try:
        steps = []
        if ";" in expr:
            equations = expr.split(";")
            results = []
            for eq in equations:
                eq = eq.strip()
                steps.append(f"Solving equation: {eq}")
                
                if "=" in eq:
                    lhs, rhs = map(sympy.sympify, eq.split("="))
                    x = symbols("x")
                    equation = Eq(lhs, rhs)
                    sol = solve(equation, x)
                    steps.append(f"Solution: x = {sol}")
                    results.append(f"x = {sol}")
                else:
                    result = sympy.sympify(eq)
                    steps.append(f"Evaluated result: {result}")
                    results.append(f"Result = {result}")
                
                steps.append("---")
            
            return {"result": "\n".join(results), "steps": steps}
        else:
            steps.append(f"Processing: {expr}")
            if "=" in expr:
                lhs, rhs = map(sympy.sympify, expr.split("="))
                x = symbols("x")
                equation = Eq(lhs, rhs)
                sol = solve(equation, x)
                steps.append(f"Solution found: x = {sol}")
                return {"result": f"x = {sol}", "steps": steps}
            else:
                result = sympy.sympify(expr)
                steps.append(f"Evaluated result: {result}")
                return {"result": f"Result = {result}", "steps": steps}
    except Exception as e:
        return {"result": f"Error: {str(e)}", "steps": ["An error occurred during calculation"]}

# Main content area
st.markdown("## 🎯 What would you like to learn today?")

# Input area based on selected feature
if feature == "📝 Smart Summarizer":
    user_input = st.text_area(
        "Enter your text to summarize:",
        height=200,
        help="Paste any text you want to summarize. Works best with 100-2000 words.",
        placeholder="Paste your text here..."
    )
    
elif feature == "🧮 Math Solver":
    st.info("💡 Tip: Separate multiple expressions with semicolons (;)")
    user_input = st.text_input(
        "Enter your mathematical expression:",
        help="Examples:\n• 2x + 3 = 7\n• 2 * (3 + 4)\n• x^2 - 4 = 0",
        placeholder="Enter your expression here..."
    )
    
else:  # Quiz Generator
    user_input = st.text_area(
        "Enter the text to generate questions from:",
        height=200,
        help="Enter the content you want to create questions about.",
        placeholder="Paste your study material here..."
    )

# Process button
if st.button("✨ Process", type="primary"):
    if not user_input.strip():
        st.warning("Please enter some content to process!")
    else:
        try:
            if feature == "📝 Smart Summarizer":
                with st.spinner("Generating summary..."):
                    summary = generate_summary(user_input)
                    st.markdown("### 📋 Summary")
                    st.markdown(f'<div class="success-box">{summary}</div>', unsafe_allow_html=True)
                    
            elif feature == "🧮 Math Solver":
                with st.spinner("Solving..."):
                    solution = solve_math(user_input)
                    st.markdown("### 📊 Solution")
                    st.markdown(f'<div class="success-box">{solution["result"]}</div>', unsafe_allow_html=True)
                    
                    with st.expander("View Step-by-Step Solution"):
                        for step in solution["steps"]:
                            st.write(step)
                    
            else:  # Quiz Generator
                with st.spinner("Generating questions..."):
                    questions = generate_quiz_questions(user_input)
                    st.markdown("### 📝 Generated Questions")
                    
                    for i, q in enumerate(questions, 1):
                        with st.expander(f"Question {i} ({q['type'].upper()})"):
                            st.markdown(f'<div class="info-box">{q["content"]}</div>', unsafe_allow_html=True)
                            
                            if q["type"] == "multiple_choice":
                                st.radio(f"Select answer for Q{i}", ["A", "B", "C", "D"], key=f"q{i}")
                            elif q["type"] == "true_false":
                                st.radio(f"Select answer for Q{i}", ["True", "False"], key=f"q{i}")
                            else:
                                st.text_input("Your answer:", key=f"q{i}")
            
            # Show original input
            with st.expander("Show Original Input"):
                st.markdown(f'<div class="warning-box">{user_input}</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.warning("Please try again with different input or settings.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Made with ❤️ by Your Smart Study Assistant</p>
        <p>Using advanced AI models to help you learn better</p>
    </div>
    """,
    unsafe_allow_html=True
)
