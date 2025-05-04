from langchain_ollama import OllamaLLM
from .summ import summarize
import requests, json, time
import re


#API CALL IMPLEMENTATION
def exam_generate_questions(question, text):
    api_url = "https://ollama-y2elcua3ga-uc.a.run.app/api/generate"
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_API_KEY",  # Uncomment if the API requires an authorization key
    }

    # Start the timer
    sum_start_time = time.time()
    
    summary = summarize(text)  # Summarize the text before passing to the generation model
    # End the timer
    sum_end_time = time.time()
    # Calculate the elapsed time in minutes
    summary_time_minutes = (sum_end_time - sum_start_time) / 60
    print(f"\nTotal Time Taken of summary: {summary_time_minutes:.2f} minutes\n")

    # Start the timer
    start_time = time.time()
    # Prompts for each type of question
    question_prompts = {
        'MCQ': """Generate {number_of_questions} multiple-choice questions at the {bloom_level} level of Bloom's Taxonomy.  

        **Bloom's Level & Key Verbs:**  
        - **Remembering (EASY):** Define, List, Recall, Identify  
        - **Understanding (MEDIUM):** Explain, Compare, Summarize, Interpret  
        - **Applying/Analyzing (HARD):** Apply, Solve, Analyze, Differentiate  
        - **Evaluating/Creating (VERY_HARD):** Justify, Critique, Design, Propose  

        **Format:**  
        Question [#]:[Full question here] 
        a) [Short Option]  
        b) [Short Option]  
        c) [Short Option]  
        d) [Short Option]  
        Correct: [letter]""",  

        'IDN': """Generate {number_of_questions} identification questions at the {bloom_level} level of Bloom's Taxonomy.  

        **Bloom's Level & Key Verbs:**  
        - **Remembering (EASY):** Name, Identify, Label, Match  
        - **Understanding (MEDIUM):** Describe, Classify, Exemplify  
        - **Applying (HARD):** Use, Demonstrate, Modify  
        - **Analyzing (VERY_HARD):** Examine, Break down, Infer  

        **Format:**  
        Question [#]: [Full specific question here] 
        Answer: [Single word answer]""",  

        'TOF': """Generate {number_of_questions} true/false statements at the {bloom_level} level of Bloom's Taxonomy.  

        **Bloom's Level & Key Verbs:**  
        - **Remembering (EASY):** Recall, Recognize  
        - **Understanding (MEDIUM):** Summarize, Interpret  
        - **Applying/Analyzing (HARD):** Apply, Investigate  
        - **Evaluating (VERY_HARD):** Judge, Defend  

        **Format:**  
        Statement [#]: [Full statement here]
        a) True  
        b) False  
        Correct: [letter]""",  

        'SHA': """Generate {number_of_questions} short-answer questions at the {bloom_level} level of Bloom's Taxonomy.  

        **Bloom's Level & Key Verbs:**  
        - **Understanding (EASY):** Explain, Paraphrase  
        - **Applying (MEDIUM):** Solve, Demonstrate  
        - **Analyzing (HARD):** Compare, Contrast  
        - **Evaluating/Creating (VERY_HARD):** Argue, Propose  

        **Format:**  
        Question [#]: [Full question here] 
        Model Answer: [2-3 sentence response demonstrating the level]""",  

        'SBQ': """Generate {number_of_questions} scenario-based questions at the {bloom_level} level of Bloom's Taxonomy.  

        **Bloom's Level & Key Verbs:**  
        - **Applying (EASY):** Implement, Operate  
        - **Analyzing (MEDIUM):** Examine, Categorize  
        - **Evaluating (HARD):** Justify, Assess  
        - **Creating (VERY_HARD):** Design, Construct  

        **Format:**  
        Scenario [#]: [Brief real-world situation]  
        Question: [Full question here] 
        """,  

        'ESS': """Generate {number_of_questions} essay questions at the {bloom_level} level of Bloom's Taxonomy.  

        **Bloom's Level & Key Verbs:**  
        - **Analyzing:** Compare, Investigate  
        - **Evaluating:** Critique, Defend  
        - **Creating:** Develop, Formulate  

        **Format:**  
        Essay question [#]: [Full question here] 
        Key Skills: [Specific cognitive skill, e.g., "Compare theories (Analyzing)"]  
        Evaluation Criteria:  
        1) [Relevance to Bloom's level]  
        2) [Depth of analysis/creativity]  
        3) [Clarity & coherence]  
        Expected Length: [Word range]  
        Model Answer: [3-5 sentence exemplar]"""  
    }

    # Get the question type abbreviation
    question_type = exam_abbreviate(question['type'])
    bloom_level = question['bloom']
    required_count = question['quantity']
    
    print(f"Generating {required_count} {bloom_level} {question_type} questions...")

    # Get the corresponding prompt for the question type
    prompt_template = question_prompts.get(question_type)
    if not prompt_template:
        print(f"No prompt template found for question type: {question_type}")
        return []

    # Format the prompt with the required number and bloom level
    prompt = prompt_template.format(number_of_questions=required_count, bloom_level=bloom_level)

    # Combine the text with the prompt
    formatted_prompt = summary + "\n\n" + prompt  # WITH SUMMARY
    print("formatted_prompt:", formatted_prompt)

    # Prepare the API payload
    payload = {
        "model": "llama3.2:3b",
        "prompt": formatted_prompt
    }

    try:
        # Make the API request
        response = requests.post(api_url, headers=headers, json=payload, stream=True)
        print("response status:", response.status_code)

        # Collect the full response from the API
        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    chunk = json.loads(line)
                    full_response += chunk.get("response", "")
                except json.JSONDecodeError:
                    print(f"Could not decode JSON: {line}")

        # Parse the generated questions
        all_generated_questions = parse_questions_and_answers(full_response)
        
        # Ensure we have exactly the required number of questions
        if len(all_generated_questions) > required_count:
            all_generated_questions = all_generated_questions[:required_count]
        
        # If we don't have enough questions, log the issue
        if len(all_generated_questions) < required_count:
            print(f"Warning: Generated only {len(all_generated_questions)} of {required_count} requested questions")

        # End the timer
        end_time = time.time()
        # Calculate the elapsed time in minutes
        elapsed_time_minutes = (end_time - start_time) / 60
        print(f"\nTotal Time Taken: {elapsed_time_minutes:.2f} minutes\n")
        print(f"Generated {len(all_generated_questions)} questions")
        print("Generated Questions:", all_generated_questions)
    except Exception as e:
        print(f"Error generating {question_type} questions: {e}")
        all_generated_questions = []

    return all_generated_questions

#OLLAMA IMPLEMENTATION
# def exam_generate_questions(questions, text):
#     llm = OllamaLLM(model="llama3.1")
#     all_generated_questions = []
    
#     summary = summarize(text) # Summarize the text before passing to the generation model
#     # Prompts for each type of question
#     question_prompts = {
#         'MCQ': """
#             You are a teacher and you have to generate an exam for your students based on the provided topic. The exam should include {number_of_questions} {difficulty} multiple-choice questions. Each question should have four options (a, b, c, d), with the correct answer specified at the end. The questions should not be overly simplistic. Follow this format:

#             Question: Write the question here, ensuring it is clear, specific, and not too common.
#             a) Option A
#             b) Option B
#             c) Option C
#             d) Option D

#             Answer: [Correct answer letter, e.g., "a"] (Provide 1-2 words max.)

#              NOTE:(Do not add unnecessary text like this: 
#                 Here are two true or false questions based on the text:
#                 Let me know if you need anything else!)
#             """,

#         'TOF': """
#             You are a teacher and you have to generate an exam for your students based on the provided topic. The exam should include {number_of_questions} {difficulty} true or false questions. Each question should be clear, specific, and not overly simplistic. Specify the correct answer at the end. Use this format:

#             Question: Write the true or false statement here.
#             a) True
#             b) False

#             Answer: [Correct answer letter, e.g., "a"] (1-2 words max.)
#             NOTE:(Do not add unnecessary text like this: 
#                 Here are two true or false questions based on the text:
#                 Let me know if you need anything else!)
#             """,

#         'IDN': """
#             You are a teacher and you have to generate an exam for your students based on the provided topic. The exam should include {number_of_questions} {difficulty} identification questions. Each question should be clear, specific, and not overly simplistic. Specify the correct answer at the end. Use this format:

#             Question: Write the identification question here, ensuring clarity and relevance.

#             Answer: [Correct answer] (not too long answer, Limit to 1-2 words.)
#              NOTE:(Do not add unnecessary text like this: 
#                 Here are two true or false questions based on the text:
#                 Let me know if you need anything else!)
#             """
#     }
#     # Loop through each selected question type and corresponding number of questions
#     for question in questions:
#         question_type = question.get('type')
#         question_type = exam_abbreviate(question_type)

#         num_questions = question.get('quantity')
#         question_difficulty = question.get('difficulty')
#         print(f"Generating {num_questions} {question_difficulty} {question_type} questions...")

#         # Get the corresponding prompt for the current question type
#         prompt_template = question_prompts.get(question_type)
#         if prompt_template:
#             # Format the prompt with the number of questions
#             prompt = prompt_template.format(number_of_questions=num_questions, difficulty=question_difficulty)

#             # Combine the text with the prompt
#             formatted_prompt = summary  + prompt # WITH SUMMARY
#             #formatted_prompt = text  + prompt  # NORMAL FEEDING

#             # Invoke the LLM (LangChain model) to generate questions
#             result = llm.invoke(formatted_prompt)

#             # Split the generated result into individual questions and answers
#             question_list = parse_questions_and_answers(result)

#             # Append the result to the list
#             all_generated_questions.append({
#                 'type': question_type,
#                 'questions': question_list
#             })

#     return all_generated_questions


#parsing depends on the question type
def parse_questions_and_answers(result):
    """
    Process the LLM result text and extract questions, options, and answers based on question type.
    Returns a list of dictionaries with question, options, and answer.
    """
    questions_and_answers = []
    lines = result.split('\n')
    current_question = {}
    current_type = ""
    
    # Identify question type based on content patterns
    if "a)" in result and "b)" in result and "c)" in result and "d)" in result:
        current_type = "MCQ"
    elif "a) True" in result and "b) False" in result:
        current_type = "TOF"
    elif "Essay Prompt" in result:
        current_type = "ESS"
    elif "Scenario" in result:
        current_type = "SBQ"
    elif "Model Answer:" in result and not "Key Skills:" in result:
        current_type = "SHA"
    else:
        current_type = "IDN"  # Default to identification if no clear pattern

    # Regular expressions for different question types
    question_patterns = {
        "standard": r"^(?:Question\s*\d*:|^\d+\.\s*Question:|^\d+\.)",
        "mcq": r"^(?:Question\s*\d*:|^\d+\.\s*Question:|^\d+\.)",
        "tof": r"^(?:Statement\s*\d*:|^\d+\.\s*Statement:|^\d+\.)",
        "essay": r"^(?:Essay Prompt\s*\d*:|^\d+\.\s*Essay Prompt:|^\d+\.)",
        "scenario": r"^(?:Scenario\s*\d*:|^\d+\.\s*Scenario:|^\d+\.)"
    }

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
            
        # Detect start of a new question based on question type
        if current_type == "MCQ" and (line.startswith("Question") or re.match(r"^\d+\.", line)):
            if current_question and 'question' in current_question:
                questions_and_answers.append(current_question)
            current_question = {'question': '', 'options': {}, 'answer': ''}
            
            # Extract question text
            if ":" in line:
                current_question['question'] = line.split(":", 1)[1].strip()
            else:
                current_question['question'] = line.split(".", 1)[1].strip()
                
        elif current_type == "TOF" and (line.startswith("Statement") or re.match(r"^\d+\.", line)):
            if current_question and 'question' in current_question:
                questions_and_answers.append(current_question)
            current_question = {'question': '', 'options': {'a': 'True', 'b': 'False'}, 'answer': ''}
            
            # Extract question text
            if ":" in line:
                current_question['question'] = line.split(":", 1)[1].strip()
            else:
                current_question['question'] = line.split(".", 1)[1].strip()
                
        elif current_type == "ESS" and (line.startswith("Essay Prompt") or re.match(r"^\d+\.", line)):
            if current_question and 'question' in current_question:
                questions_and_answers.append(current_question)
            current_question = {'question': '', 'options': {}, 'answer': ''}
            
            # Extract question text
            if ":" in line:
                current_question['question'] = line.split(":", 1)[1].strip()
            else:
                current_question['question'] = line.split(".", 1)[1].strip()
                
        elif current_type == "SBQ" and (line.startswith("Scenario") or re.match(r"^\d+\.", line)):
            if current_question and 'question' in current_question:
                questions_and_answers.append(current_question)
            current_question = {'question': 'Scenario: ', 'options': {}, 'answer': ''}
            
            # Extract scenario text
            if ":" in line:
                current_question['question'] += line.split(":", 1)[1].strip() + "\n"
            else:
                current_question['question'] += line.split(".", 1)[1].strip() + "\n"
            
            # Move to the next line to get the question
            i += 1
            if i < len(lines) and lines[i].strip().startswith("Question:"):
                current_question['question'] += "Question: " + lines[i].strip().split(":", 1)[1].strip()
                
        elif current_type == "IDN" and (line.startswith("Question") or re.match(r"^\d+\.", line)):
            if current_question and 'question' in current_question:
                questions_and_answers.append(current_question)
            current_question = {'question': '', 'options': {}, 'answer': ''}
            
            # Extract question text
            if ":" in line:
                current_question['question'] = line.split(":", 1)[1].strip()
            else:
                current_question['question'] = line.split(".", 1)[1].strip()
                
        elif current_type == "SHA" and (line.startswith("Question") or re.match(r"^\d+\.", line)):
            if current_question and 'question' in current_question:
                questions_and_answers.append(current_question)
            current_question = {'question': '', 'options': {}, 'answer': ''}
            
            # Extract question text
            if ":" in line:
                current_question['question'] = line.split(":", 1)[1].strip()
            else:
                current_question['question'] = line.split(".", 1)[1].strip()
        
        # Parse options for MCQ questions
        elif current_type == "MCQ" and re.match(r"^[a-d]\)", line):
            option_letter = line[0]
            option_text = line[2:].strip()
            if current_question:
                current_question['options'][option_letter] = option_text
        
        # Parse answers for all question types
        elif line.startswith("Answer:") or line.startswith("Correct:") or line.startswith("Model Answer:") or line.startswith("Model Response:"):
            if current_question:
                if ":" in line:
                    answer_text = line.split(":", 1)[1].strip()
                    # For T/F and MCQ, we only need the letter
                    if current_type in ["MCQ", "TOF"] and "–" in answer_text:
                        answer_letter = answer_text.split("–")[0].strip()
                        current_question['answer'] = answer_letter
                    else:
                        current_question['answer'] = answer_text
                        
                # Continue collecting multi-line answers
                i += 1
                while i < len(lines) and not (
                    lines[i].startswith("Question") or 
                    lines[i].startswith("Statement") or
                    lines[i].startswith("Essay Prompt") or
                    lines[i].startswith("Scenario") or
                    re.match(r"^\d+\.", lines[i])
                ):
                    if lines[i].strip() and not lines[i].startswith("Key Skills:") and not lines[i].startswith("Evaluation Criteria:"):
                        current_question['answer'] += " " + lines[i].strip()
                    i += 1
                i -= 1  # Go back one line since we'll increment i at the end of the loop
        
        i += 1

    # Add the last question
    if current_question and 'question' in current_question:
        questions_and_answers.append(current_question)

    return questions_and_answers

def exam_abbreviate(q_type):
    return {
        'identification': 'IDN',
        'multiple_choice': 'MCQ',
        'true_false': 'TOF',
        'situation_based_questions': 'SBQ',
        'essay': 'ESS',
        'short_answer': 'SHA',
        }.get(q_type.lower(), 'TOF') # default true or false