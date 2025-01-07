from langchain_ollama import OllamaLLM
from .summ import summarize
import time

def keynote_generation(keynotes, text):
    llm = OllamaLLM(model="llama3.1")

    generated_keynotes = []

    keynote_prompt = """
    Objective: You are a Teacher. Create a concise and comprehensive student reviewer for the following topic:

    Structure:

    Learning Objectives:

    Clearly state 2-3 learning objectives students should achieve after reviewing this material.
    Overview:

    Title and Overview: Clearly state the subject name and provide an outline of the topics covered.
    Key Concepts or Summary: Present the main points of each topic in bullet points, tables, or charts. Include essential definitions, formulas, or dates.

    Provide a concise and engaging summary of the topic.
    Key Terms and Definitions:

    List and define key terms relevant to the topic. Definitions should be concise and student-friendly.
    Examples:

    Include relevant examples to illustrate key concepts or applications of the topic.
    Tips:

    Offer practical tips for understanding, remembering, or applying the material(mnemonics).
    """
    # Combine the prompt with the input text
    prompt_template = keynote_prompt + text

    # Start the timer
    start_time = time.time()

    # Invoke the LLM with the combined prompt
    result = llm.invoke(prompt_template)

    # Debugging output for the result
    print("Generated Keynotes:", result)

    # End the timer
    end_time = time.time()
    elapsed_time_minutes = (end_time - start_time) / 60
    print(f"Total Time Taken: {elapsed_time_minutes:.2f} minutes")

    return result

def clean_text(text):
    """
    Removes unnecessary formatting symbols such as ** and ## from the text.
    Args:
        text (str): Raw text from LLM
    Returns:
        str: Cleaned text without ** and ##
    """
    return text.replace("**", "").replace("##", "")


def format_keynotes(text):
    """
    Parse and format the LLM-generated keynotes text into structured HTML.
    Args:
        text (str): Raw text from LLM
    Returns:
        str: Formatted HTML string
    """
    # Preprocess the text to remove unwanted symbols
    text = clean_text(text)
    
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
        if any(header in line for header in ["Learning Objectives:", "Overview:", "Key Concepts or Summary:", 
               "Concise Summary", "Key Terms and Definitions:", "Examples:", "Tips:", "Additional Resources:"]):
            # Close the previous section, if any
            if current_section:
                sections.append(current_section + '</div></div>')
                current_section = ""
            
            # Start a new section
            current_section = f'<div class="section"><h3 class="section-title">{line}</h3><div class="section-content">'
        
        # Handle numbered lists (Learning Objectives, Tips)
        elif line[0].isdigit() and '. ' in line:
            number, content = line.split('. ', 1)
            current_section += f'<div class="numbered-item"><span class="number">{number}.</span> {content}</div>'
        
        # Handle bullet points
        elif line.startswith('* '):
            content = line[2:]
            current_section += f'<div class="bullet-item">{content}</div>'
        
        # # Handle tables
        # elif '|' in line:
        #     if '---' not in line:  # Skip table separator lines
        #         cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        #         if len(cells) >= 2:
        #             if current_section.endswith('</table>') is False:  # Start a new table
        #                 current_section += '<table class="keynotes-table">'
        #             if "Key Points" in line:  # Table header
        #                 current_section += '<tr>'
        #                 for cell in cells:
        #                     current_section += f'<th>{cell}</th>'
        #                 current_section += '</tr>'
        #             else:  # Table content
        #                 current_section += '<tr>'
        #                 for cell in cells:
        #                     current_section += f'<td>{cell}</td>'
        #                 current_section += '</tr>'
        
        # Handle key terms
        elif ': ' in line and not line.startswith('Title:'):
            term, definition = line.split(': ', 1)
            current_section += f'<div class="key-term"><span class="term">{term}:</span> {definition}</div>'
        
        # Handle regular text
        else:
            current_section += f'<p>{line}</p>'
    
    # Add the last section
    if current_section:
        sections.append(current_section + '</div></div>')
    
    # Combine all sections
    formatted_html = '<div class="keynotes-wrapper">' + ''.join(sections) + '</div>'
    
    return formatted_html
