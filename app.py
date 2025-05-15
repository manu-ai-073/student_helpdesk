def generate_summary(text):
    """Generate summary using DistilBART CNN with improved parameters"""
    length_map = {
        "Very Short": 50,
        "Short": 100,
        "Medium": 150,
        "Long": 250
    }
    
    max_length = length_map[summary_length]
    
    # Improved parameters for better summarization
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": max_length,
            "min_length": max_length // 3,  # Allow for shorter summaries
            "length_penalty": 2.0,  # Encourage more concise summaries
            "num_beams": 4,         # Use beam search for better quality
            "early_stopping": True,
            "do_sample": False      # Deterministic output
        }
    }
    
    result = query_model(payload)
    if result and isinstance(result, list):
        return result[0]['summary_text']
    return "Error generating summary."

def generate_quiz_questions(text):
    """Generate questions with improved answer checking"""
    questions = []
    # First get a good summary of the text
    summary_payload = {
        "inputs": text,
        "parameters": {
            "max_length": 150,
            "min_length": 50,
            "num_beams": 4,
            "length_penalty": 2.0,
            "do_sample": False
        }
    }
    
    summary_result = query_model(summary_payload)
    if not summary_result:
        return []
        
    # Extract key points from the summary
    summary = summary_result[0]['summary_text']
    key_points = [s.strip() for s in summary.split('.') if len(s.strip()) > 20]
    
    if not key_points:
        key_points = [summary]
    
    for i in range(min(num_questions, len(key_points))):
        point = key_points[i]
        
        for q_type in question_type:
            if q_type == "Multiple Choice":
                # Create distractors by modifying the correct answer
                correct_answer = point
                options = [
                    correct_answer,
                    f"Not true: {correct_answer}",
                    f"The opposite of: {correct_answer}",
                    "None of the above"
                ]
                random.shuffle(options)  # Randomize option order
                
                question = {
                    "type": "multiple_choice",
                    "question": "Based on the text, which statement is correct?",
                    "options": options,
                    "correct_answer": correct_answer
                }
                questions.append(question)
                
            elif q_type == "True/False":
                # Generate a true/false question
                is_true = random.choice([True, False])
                statement = point if is_true else f"Not true: {point}"
                
                question = {
                    "type": "true_false",
                    "question": f"Is this statement true or false: {statement}",
                    "correct_answer": "True" if is_true else "False"
                }
                questions.append(question)
                
            elif q_type == "Fill in the Blank":
                # Create a fill in the blank by removing a key word
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

# In the main UI section, update the quiz rendering part:
else:  # Quiz Generator
    with st.spinner("Generating questions..."):
        questions = generate_quiz_questions(user_input)
        if questions:
            st.markdown("### 📝 Generated Questions")
            
            # Create a form for the quiz
            with st.form("quiz_form"):
                for i, q in enumerate(questions, 1):
                    st.markdown(f"### Question {i}")
                    st.markdown(f"**{q['question']}**")
                    
                    if q['type'] == 'multiple_choice':
                        answer = st.radio(
                            "Choose your answer:",
                            q['options'],
                            key=f"q{i}"
                        )
                        # Store the correct answer in session state
                        st.session_state[f"correct_answer_{i}"] = q['correct_answer']
                        st.session_state[f"answer_{i}"] = answer
                        
                    elif q['type'] == 'true_false':
                        answer = st.radio(
                            "Select True or False:",
                            ["True", "False"],
                            key=f"q{i}"
                        )
                        st.session_state[f"correct_answer_{i}"] = q['correct_answer']
                        st.session_state[f"answer_{i}"] = answer
                        
                    else:  # fill_blank
                        answer = st.text_input(
                            "Fill in the blank:",
                            key=f"q{i}"
                        )
                        st.session_state[f"correct_answer_{i}"] = q['correct_answer']
                        st.session_state[f"answer_{i}"] = answer
                    
                    st.markdown("---")
                
                # Submit button for the entire quiz
                submitted = st.form_submit_button("Check Answers")
                
                if submitted:
                    score = 0
                    for i in range(1, len(questions) + 1):
                        user_answer = st.session_state.get(f"answer_{i}")
                        correct_answer = st.session_state.get(f"correct_answer_{i}")
                        
                        if questions[i-1]['type'] == 'fill_blank':
                            is_correct = user_answer.lower().strip() == correct_answer.lower().strip()
                        else:
                            is_correct = user_answer == correct_answer
                        
                        if is_correct:
                            score += 1
                            st.success(f"Question {i}: Correct! ✅")
                        else:
                            st.error(f"Question {i}: Incorrect ❌. The correct answer was: {correct_answer}")
                    
                    # Show final score
                    st.markdown(f"### Final Score: {score}/{len(questions)}")
                    percentage = (score / len(questions)) * 100
                    st.progress(percentage / 100)
                    
                    if percentage == 100:
                        st.balloons()
                        st.success("Perfect Score! 🎉")
                    elif percentage >= 70:
                        st.success("Great job! 👏")
                    elif percentage >= 50:
                        st.info("Good effort! Keep practicing! 💪")
                    else:
                        st.warning("Keep studying! You'll do better next time! 📚")
        else:
            st.error("Failed to generate questions. Please try again with different text.")
