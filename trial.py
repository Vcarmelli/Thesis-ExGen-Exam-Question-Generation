import requests
import json
from PyPDF2 import PdfReader
from docx import Document
import time  # Import for timing

def extract_text_from_file(file_path):
    """Extract text from .txt, .pdf, or .docx files."""
    if file_path.endswith(".txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error reading text file: {e}")
    elif file_path.endswith(".pdf"):
        try:
            pdf_reader = PdfReader(file_path)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {e}")
    elif file_path.endswith(".docx"):
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            raise ValueError(f"Error reading Word file: {e}")
    else:
        raise ValueError("Unsupported file type. Please use a .txt, .pdf, or .docx file.")

# Get the file path from the user
file_path = input("Enter the path to the text, PDF, or Word file to generate questions from: ")

try:
    # Start timing for extraction
    start_extraction = time.time()
    file_content = extract_text_from_file(file_path)
    end_extraction = time.time()
except Exception as e:
    print(e)
    exit()

# Print the extracted file content and duration
print("\nExtracted File Content:\n")
print(file_content)
print("\nEnd of File Content\n")
print(f"Time taken to extract content: {end_extraction - start_extraction:.2f} seconds\n")

# Ask the user to confirm before proceeding
proceed = input("Do you want to proceed with this content? (yes/no): ").strip().lower()
if proceed != "yes":
    print("Operation canceled.")
    exit()

# API details
url = "https://ollama-y2elcua3ga-uc.a.run.app/api/generate"
headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer YOUR_API_KEY",  # Uncomment if required
}

# Payload with the extracted file content as the input prompt
payload = {
    "model": "llama3.2:3b",
    "prompt": f"Based on the following text, create 10 Multiple Choice questions:\n\n{file_content}"
}

# Start timing for question generation
start_generation = time.time()
response = requests.post(url, headers=headers, json=payload, stream=True)
end_generation = time.time()

try:
    # Initialize a variable to store the full response
    full_response = ""

    # Read the response stream line by line
    for line in response.iter_lines(decode_unicode=True):
        if line:
            # Parse each line as JSON
            chunk = json.loads(line)
            # Extract the 'response' key and append it to the full response
            full_response += chunk.get("response", "")

    # Print the generated questions and duration
    print("\nGenerated Questions:\n", full_response)
    print(f"\nTime taken to generate questions: {end_generation - start_generation:.2f} seconds")
except Exception as e:
    print("Error processing the response:", e)