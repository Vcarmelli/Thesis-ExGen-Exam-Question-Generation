#from langchain_ollama import OllamaLLM
from .summ import summarize
import time, requests, json

# def keynote_generation(keynotes, text):
#     llm = OllamaLLM(model="llama3.1")

#     generated_keynotes = []

#     keynote_prompt = """
#     Objective: You are a Teacher. Create a concise and comprehensive student reviewer for the following topic:

#     Structure:

#     Learning Objectives:

#     Clearly state 2-3 learning objectives students should achieve after reviewing this material.
#     Overview:

#     Title and Overview: Clearly state the subject name and provide an outline of the topics covered.
#     Key Concepts or Summary: Present the main points of each topic in bullet points, tables, or charts. Include essential definitions, formulas, or dates.

#     Provide a concise and engaging summary of the topic.
#     Key Terms and Definitions:

#     List and define key terms relevant to the topic. Definitions should be concise and student-friendly.
#     Examples:

#     Include relevant examples to illustrate key concepts or applications of the topic.
#     Tips:

#     Offer practical tips for understanding, remembering, or applying the material(mnemonics).
#     """
#     # Combine the prompt with the input text
#     prompt_template = keynote_prompt + text

#     # Start the timer
#     start_time = time.time()

#     # Invoke the LLM with the combined prompt
#     result = llm.invoke(prompt_template)

#     # Debugging output for the result
#     print("Generated Keynotes:", result)

#     # End the timer
#     end_time = time.time()
#     elapsed_time_minutes = (end_time - start_time) / 60
#     print(f"Total Time Taken: {elapsed_time_minutes:.2f} minutes")

#     return result

def keynote_generation(keynotes, text):
    api_url = "https://ollama-y2elcua3ga-uc.a.run.app/api/generate"
    headers = {
        "Content-Type": "application/json",
    }

    keynote_prompt = """
    **Objective:** You are a Teacher. Create a concise and comprehensive reviewer for students based on the following guidelines:
    1. **Learning Objectives:**
    * Identify 2–3 clear learning objectives students should achieve after studying this material.
    2. **Overview:**
    * Provide the subject name and an outline of the topics covered.
    3. **Summary:**
    * Write a concise, engaging summary of the topic.
    * Highlight the main points in bullet points, tables, or charts where applicable.
    * Include key definitions, formulas, names, or dates.
    4. **Key Terms and Definitions:**
    * List essential terms relevant to the topic with concise, student-friendly definitions.
    5. **Examples:**
    * Provide relevant examples to illustrate key concepts or their applications.
    6. **Tips:**
    * Share practical tips to help students understand, remember, or apply the material (e.g., mnemonics or memory aids).
    Focus on brevity and clarity. Use **bullets**, not numbers, for keynotes. Avoid unnecessary elaboration.
    """
    
    # Combine the prompt with the input text
    prompt_template = keynote_prompt + text

    start_time = time.time()

    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt_template,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        result = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                chunk = json.loads(line)
                result += chunk.get("response", "")
    except Exception as e:
        print(f"Error generating keynotes")

    end_time = time.time()
    elapsed_time_minutes = (end_time - start_time) / 60 
    print("generated keynotes:", result)
    print(f"Total Time Taken: {elapsed_time_minutes:.2f} minutes")
    

    return result

def clean_text(text):
    """
    Clean the text by removing AI-generated preambles and formatting artifacts.
    """
    # List of common preamble phrases to remove
    preambles = [
        "I see that the text provided",
        "However, if you would like",
        "Here is a rewritten version:",
        "I can help create",
        "Let me create",
        "Here's a student reviewer",
        "Based on the guidelines provided",
        "I'll create a review"
    ]
    
    # Split text into lines
    lines = text.split('\n')
    cleaned_lines = []
    content_started = False
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Skip lines containing preamble phrases
        if any(preamble in line for preamble in preambles):
            continue
            
        # Start capturing content when we see a section header or "Subject:"
        if ("Subject:" in line or 
            any(header in line for header in ["Learning Objectives:", "Overview:", 
                                            "Summary:", "Key Terms and Definitions:", 
                                            "Examples:", "Tips:"])):
            content_started = True
            
        if content_started:
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines)

def format_keynotes(text):
    """
    Parse and format the LLM-generated keynotes text into structured HTML.
    """
    # Clean the text first
    text = clean_text(text)
    text = text.replace('**', '')  # Remove all ** symbols
    
    sections = []
    current_section = ""
    
    # Split text into lines and process each line
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Handle main section headers
        if any(header in line for header in ["Learning Objectives:", "Overview:", 
               "Summary:", "Key Terms and Definitions:", "Examples:", "Tips:"]):
            if current_section:
                sections.append(current_section + '</div></div>')
                current_section = ""
            current_section = f'<div class="section"><h3 class="section-title">{line}</h3><div class="section-content">'
        
        # Handle bullet points (convert all list markers to bullets)
        elif line.startswith(('-', '+', '*', '•')) or (len(line) > 2 and line[0].isdigit() and line[1] == '.'):
            content = line.lstrip('-+*• 0123456789.')
            # Check if the line contains a term definition
            if ': ' in content and not content.startswith('Title:'):
                term, definition = content.split(': ', 1)
                current_section += f'<div class="bullet-item"><strong>{term}</strong>: {definition}</div>'
            else:
                current_section += f'<div class="bullet-item">{content}</div>'
        
        # Handle regular text
        else:
            current_section += f'<p>{line}</p>'
    
    # Add the last section
    if current_section:
        sections.append(current_section + '</div></div>')
    
    # Combine all sections
    formatted_html = '<div class="keynotes-wrapper">' + ''.join(sections) + '</div>'
    
    return formatted_html
