# Import necessary libraries
from .summ import summarize
import requests, json, time
import re

# Generate prompt functions for each question type
def generate_mcq_prompt(number_of_questions, bloom_level):
    return f"""Generate {number_of_questions} multiple-choice questions at the {bloom_level} level of Bloom's Taxonomy.

**Bloom's Levels:**
- **EASY:** Questions that test recall of specific facts or basic concepts
- **MEDIUM:** Questions that test comprehension and interpretation
- **HARD:** Questions requiring application of knowledge or analysis
- **VERY_HARD:** Questions demanding evaluation or creation of perspectives

**Format each question as:**
Question {{num}}: [Clear, specific question text]
a) [Option text]
b) [Option text]
c) [Option text]
d) [Option text]
Correct: [letter only]
"""

def generate_idn_prompt(number_of_questions, bloom_level):
    return f"""Generate {number_of_questions} identification questions at the {bloom_level} level of Bloom's Taxonomy.

**Bloom's Levels:**
- **EASY:** Questions asking to identify specific terms or concepts
- **MEDIUM:** Questions requiring explanation of concepts
- **HARD:** Questions requiring application to new situations
- **VERY_HARD:** Questions demanding deeper analysis

**Format each question as:**
Question {{num}}: [Clear identification question]
Answer: [Brief, precise answer]
"""

def generate_tof_prompt(number_of_questions, bloom_level):
    return f"""Generate {number_of_questions} true/false statements at the {bloom_level} level of Bloom's Taxonomy.

**Bloom's Levels:**
- **EASY:** Statements testing recall of basic facts
- **MEDIUM:** Statements requiring comprehension of relationships
- **HARD:** Statements requiring application or analysis
- **VERY_HARD:** Statements requiring evaluation of information

**Format each statement as:**
Statement {{num}}: [Clear true or false statement]
a) True
b) False
Correct: [letter only]
"""

def generate_sha_prompt(number_of_questions, bloom_level):
    return f"""Generate {number_of_questions} short-answer questions at the {bloom_level} level of Bloom's Taxonomy.

**Bloom's Levels:**
- **EASY:** Questions requiring brief explanation
- **MEDIUM:** Questions requiring application to specific situations
- **HARD:** Questions requiring analysis of relationships
- **VERY_HARD:** Questions requiring evaluation or creation

**Format each question as:**
Question {{num}}: [Short answer question text]
Model Answer: [2-4 sentence response]
"""

def generate_sbq_prompt(number_of_questions, bloom_level):
    return f"""Generate {number_of_questions} scenario-based questions at the {bloom_level} level of Bloom's Taxonomy.

**Bloom's Levels:**
- **EASY:** Simple application of concepts to situations
- **MEDIUM:** Analysis of relationships in realistic contexts
- **HARD:** Evaluation of solutions in complex scenarios
- **VERY_HARD:** Creation of novel approaches to challenging situations

**Format each question as:**
Scenario {{num}}: [Brief situation related to content]
Question: [Specific question about the scenario]
Answer: [3-5 sentence answer about the situation]
"""

def generate_ess_prompt(number_of_questions, bloom_level):
    return f"""Generate {number_of_questions} essay questions at the {bloom_level} level of Bloom's Taxonomy.

**Bloom's Levels:**
- **ANALYZING:** Break down concepts and examine relationships
- **EVALUATING:** Assess ideas against criteria and make judgments
- **CREATING:** Synthesize information to develop original solutions

**Format each question as:**
Essay Question {{num}}: [Open-ended question requiring extended response]
Full answer: [Full answer to the question]
"""

# Main function to generate exam questions
def exam_generate_questions(question, text):
    api_url = "https://ollama-y2elcua3ga-uc.a.run.app/api/generate"
    headers = {
        "Content-Type": "application/json"
    }

    # Start the timer for summarization
    sum_start_time = time.time()
    
    # Summarize the text before passing to the generation model
    summary = summarize(text)
    
    # End the timer and calculate elapsed time
    sum_end_time = time.time()
    summary_time_minutes = (sum_end_time - sum_start_time) / 60
    print(f"\nTotal Time Taken of summary: {summary_time_minutes:.2f} minutes\n")

    # Start the timer for question generation
    start_time = time.time()
    
    # Get the question type abbreviation
    question_type = exam_abbreviate(question['type'])
    bloom_level = question['bloom']
    required_count = question['quantity']
    
    print(f"Generating {required_count} {bloom_level} {question_type} questions...")

    # Get the corresponding prompt based on question type
    formatted_prompt = ""
    if question_type == 'MCQ':
        formatted_prompt = summary + "\n\n" + generate_mcq_prompt(required_count, bloom_level)
    elif question_type == 'IDN':
        formatted_prompt = summary + "\n\n" + generate_idn_prompt(required_count, bloom_level)
    elif question_type == 'TOF':
        formatted_prompt = summary + "\n\n" + generate_tof_prompt(required_count, bloom_level)
    elif question_type == 'SHA':
        formatted_prompt = summary + "\n\n" + generate_sha_prompt(required_count, bloom_level)
    elif question_type == 'SBQ':
        formatted_prompt = summary + "\n\n" + generate_sbq_prompt(required_count, bloom_level)
    elif question_type == 'ESS':
        formatted_prompt = summary + "\n\n" + generate_ess_prompt(required_count, bloom_level)
    else:
        print(f"No prompt template found for question type: {question_type}")
        return []

    print("Using formatted prompt:", formatted_prompt)

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

        # End the timer and calculate elapsed time
        end_time = time.time()
        elapsed_time_minutes = (end_time - start_time) / 60
        print(f"\nTotal Time Taken: {elapsed_time_minutes:.2f} minutes\n")
        print(f"Generated {len(all_generated_questions)} questions")
        print(full_response)
        
    except Exception as e:
        print(f"Error generating {question_type} questions: {e}")
        all_generated_questions = []

    return all_generated_questions

# Keep the existing helper functions
def exam_abbreviate(q_type):
    return {
        'identification': 'IDN',
        'multiple_choice': 'MCQ',
        'true_false': 'TOF',
        'situation_based_questions': 'SBQ',
        'essay': 'ESS',
        'short_answer': 'SHA',
    }.get(q_type.lower(), 'TOF')  # default true or false

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
    elif "Essay Question" in result:
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
        "essay": r"^(?:Essay Question\s*\d*:|^\d+\.\s*Essay Question:|^\d+\.)",
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
                
        elif current_type == "ESS" and (line.startswith("Essay Question") or re.match(r"^\d+\.", line)):
            if current_question and 'question' in current_question:
                questions_and_answers.append(current_question)

            current_question = {
                'question': '',
                'options': {},
                'answer': ''
            }

            # Start collecting question text
            question_lines = []

            if ":" in line:
                question_lines.append(line.split(":", 1)[1].strip())
            else:
                question_lines.append(line.split(".", 1)[1].strip())

            i += 1
            # Move through lines to find 'Full answer:' section
            while i < len(lines):
                subline = lines[i].strip()

                if subline.startswith("Essay Question") or re.match(r"^\d+\.", subline):
                    i -= 1  # step back for next iteration
                    break

                if subline.startswith("Full answer:"):
                    i += 1
                    break  # move to collecting the answer

                # Continue gathering question text
                question_lines.append(subline)
                i += 1

            # Collect full answer
            full_answer_lines = []
            while i < len(lines):
                subline = lines[i].strip()
                if subline.startswith("Essay Question") or re.match(r"^\d+\.", subline):
                    i -= 1  # prepare for next
                    break
                full_answer_lines.append(subline)
                i += 1

            current_question['question'] = "\n".join(question_lines).strip()
            current_question['answer'] = "\n".join(full_answer_lines).strip()
            questions_and_answers.append(current_question)


                
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
                    lines[i].startswith("Essay Question") or
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