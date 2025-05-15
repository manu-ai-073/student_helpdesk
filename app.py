import streamlit as st
import requests
import sympy
from sympy import symbols, Eq, solve
import time
import random

# Configure page
st.set_page_config(
    page_title="🎓 Smart Study Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .question-box {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Load Hugging Face Token from secrets
API_TOKEN = st.secrets["HF_TOKEN"]
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Updated Models configuration with verified working model
MODEL = "sshleifer/distilbart-cnn-12-6"  # Lighter and faster version of BART

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
        
    elif feature == "❓ Quiz Generator":
        st.markdown("### Quiz Settings")
        num_questions = st.slider("Number of Questions", 1, 5, 3)
        question_type = st.multiselect(
            "Question Types",
            ["Multiple Choice", "True/False", "Fill in the Blank"],
            default=["Multiple Choice"]
        )

def query_model(payload, max_retries=3):
    """Enhanced model query with better error handling"""
    url = f"https://api-inference.huggingface.co/models/{MODEL}"
    
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
    """Generate summary using DistilBART CNN"""
    length_map = {
        "Very Short": 50,
        "Short": 100,
        "Medium": 150,
        "Long": 250
    }
    
    max_length = length_map[summary_length]
    
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": max_length,
            "min_length": max_length // 2,
            "do_sample": False,
            "early_stopping": True
        }
    }
    
    result = query_model(payload)
    if result and isinstance(result, list):
        return result[0]['summary_text']
    return "Error generating summary."

def extract_key_points(text):
    """Extract key points from text using summarization"""
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": 100,
            "min_length": 30,
            "do_sample": True,
            "num_beams": 4,
            "temperature": 0.7,
        }
    }
    
    result = query_model(payload)
    if result and isinstance(result, list):
        summary = result[0]['summary_text']
        # Split into sentences and clean up
        points = [s.strip() for s in summary.split('.') if s.strip()]
        return points
    return []

def generate_quiz_questions(text):
    """Generate questions based on key points"""
    questions = []
    key_points = extract_key_points(text)
    
    if not key_points:
        return []
    
    for _ in range(min(num_questions, len(key_points))):
        point = random.choice(key_points)
        key_points.remove(point)  # Avoid duplicate questions
        
        for q_type in question_type:
            if q_type == "Multiple Choice":
                # Generate a multiple choice question
                question = {
                    "type": "multiple_choice",
                    "question": f"Which of the following is true about the text?",
                    "correct_answer": point,
                    "options": [
                        point,
                        f"The opposite of {point}",
                        f"Something unrelated to {point}",
                        "None of the above"
                    ]
                }
                questions.append(question)
                
            elif q_type == "True/False":
                # Generate a true/false question
                question = {
                    "type": "true_false",
                    "question": f"Is the following statement true or false: {point}",
                    "correct_answer": "True"
                }
                questions.append(question)
                
            elif q_type == "Fill in the Blank":
                # Create a fill in the blank question
                words = point.split()
                if len(words) > 3:
                    blank_idx = random.randint(1, len(words) - 2)
                    answer = words[blank_idx]
                    words[blank_idx] = "_____"
                    question = {
                        "type": "fill_blank",
                        "question": " ".join(words),
                        "correct_answer": answer
                    }
                    questions.append(question)
    
    return questions

def solve_math(expr):
    """Math solver with step-by-step solutions"""
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
                    if questions:
                        st.markdown("### 📝 Generated Questions")
                        
                        for i, q in enumerate(questions, 1):
                            with st.expander(f"Question {i}"):
                                st.markdown(f'<div class="question-box">')
                                st.markdown(f"**{q['question']}**")
                                
                                if q['type'] == 'multiple_choice':
                                    choice = st.radio(
                                        "Select your answer:",
                                        q['options'],
                                        key=f"q{i}"
                                    )
                                    if st.button("Check Answer", key=f"check{i}"):
                                        if choice == q['correct_answer']:
                                            st.success("Correct! 🎉")
                                        else:
                                            st.error(f"Incorrect. The correct answer is: {q['correct_answer']}")
                                            
                                elif q['type'] == 'true_false':
                                    choice = st.radio(
                                        "Select your answer:",
                                        ["True", "False"],
                                        key=f"q{i}"
                                    )
                                    if st.button("Check Answer", key=f"check{i}"):
                                        if choice == q['correct_answer']:
                                            st.success("Correct! 🎉")
                                        else:
                                            st.error(f"Incorrect. The correct answer is: {q['correct_answer']}")
                                            
                                else:  # fill_blank
                                    answer = st.text_input("Your answer:", key=f"q{i}")
                                    if st.button("Check Answer", key=f"check{i}"):
                                        if answer.lower() == q['correct_answer'].lower():
                                            st.success("Correct! 🎉")
                                        else:
                                            st.error(f"Incorrect. The correct answer is: {q['correct_answer']}")
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("Failed to generate questions. Please try again with different text.")
            
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
