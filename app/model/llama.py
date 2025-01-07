from langchain_ollama import OllamaLLM
from .summ import summarize
import requests, json, time


#API CALL IMPLEMENTATION
def exam_generate_questions(questions, text):
    api_url = "https://ollama-y2elcua3ga-uc.a.run.app/api/generate"
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_API_KEY",  # Uncomment if the API requires an authorization key
    }
    all_generated_questions = []

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
        'MCQ': """
            You are a teacher and you have to generate an exam for your students based on the provided topic. The exam should include {number_of_questions} {difficulty} multiple-choice questions. Each question should have four options (a, b, c, d), with the correct answer specified at the end. The questions should not be overly simplistic. Follow this format:

            Question: Write the question here, ensuring it is clear, specific, and not too common.
            a) Option A
            b) Option B
            c) Option C
            d) Option D

            Answer: [Correct answer letter, e.g., "a"] (Provide 1-2 words max.)
            if it is a sensitive topic, please still generate the questions and answer.
            """,

        'TOF': """
            You are a teacher and you have to generate an exam for your students based on the provided topic. The exam should include {number_of_questions} {difficulty} true or false questions. Each question should be clear, specific, and not overly simplistic. Specify the correct answer at the end. Use this format:

            Question: Write the true or false statement here.
            a) True
            b) False

            Answer: [Correct answer letter, e.g., "a"] (1-2 words max.)
            if it is a sensitive topic, please still generate the questions and answer.
            """,

        'IDN': """
            You are a teacher and you have to generate an exam for your students based on the provided topic. The exam should include {number_of_questions} {difficulty} identification questions. Each question should be clear, specific, and not overly simplistic. Specify the correct answer at the end. Use this format:

            Question: Write the identification question here, ensuring clarity and relevance.

            Answer: [Correct answer] (not too long answer, Limit to 1-2 words.)
            if it is a sensitive topic, please still generate the questions and answer.
            """
    }

    for question in questions:
        question_type = question.get('type')
        question_type = exam_abbreviate(question_type)

        num_questions = question.get('quantity')
        question_difficulty = question.get('difficulty')

        print(f"Generating {num_questions} {question_difficulty} {question_type} questions...")

        # Get the corresponding prompt for the current question type
        prompt_template = question_prompts.get(question_type)
        if prompt_template:
            # Format the prompt with the number of questions
            prompt = prompt_template.format(number_of_questions=num_questions, difficulty=question_difficulty)

            # Combine the text with the prompt
            formatted_prompt = summary + prompt  # WITH SUMMARY

            # Prepare the API payload
            payload = {
                "model": "llama3.2:3b",
                "prompt": formatted_prompt
            }

            try:
                # Make the API request
                response = requests.post(api_url, headers=headers, json=payload, stream=True)

                # Collect the full response from the API
                full_response = ""
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        chunk = json.loads(line)
                        full_response += chunk.get("response", "")

                # Parse the generated questions and append to the list
                question_list = parse_questions_and_answers(full_response)
                all_generated_questions.append({
                    'type': question_type,
                    'questions': question_list
                })

            except Exception as e:
                print(f"Error generating {question_type} questions: {e}")

    # End the timer
    end_time = time.time()

    # Calculate the elapsed time in minutes
    elapsed_time_minutes = (end_time - start_time) / 60
    print(f"\nTotal Time Taken: {elapsed_time_minutes:.2f} minutes\n")
    print(full_response)

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



def parse_questions_and_answers(result):
    # This function processes the result and splits questions, options, and answers
    questions_and_answers = []
    lines = result.split('\n')

    current_question = ""
    options = {}
    current_answer = ""

    for line in lines:
        if line.startswith("Question:"):
            # New question starts
            if current_question:
                questions_and_answers.append({
                    'question': current_question.strip(),
                    'options': options,  # Add options
                    'answer': current_answer.strip()
                })
            current_question = line.replace("Question:", "").strip()
            options = {}  # Reset options for the new question
            current_answer = ""  # Reset answer for the new question
        elif line.startswith("a)") or line.startswith("b)") or line.startswith("c)") or line.startswith("d)"):
            # Capture options a), b), c), d)
            option_letter = line[0]  # a, b, c, d
            option_text = line[3:].strip()  # Extract the option text
            options[option_letter] = option_text  # Save it as part of the options dictionary
        elif line.startswith("Answer:"):
            current_answer = line.replace("Answer:", "").strip()

    # Add the last question
    if current_question:
        questions_and_answers.append({
            'question': current_question.strip(),
            'options': options,  # Add options
            'answer': current_answer.strip()
        })

    return questions_and_answers

def exam_abbreviate(q_type):
    return {'identification': 'IDN', 'multiple_choice': 'MCQ', 'true_or_false': 'TOF'}.get(q_type.lower(), 'UNKNOWN')