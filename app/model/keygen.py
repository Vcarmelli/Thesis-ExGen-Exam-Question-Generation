from langchain_ollama import OllamaLLM
from .summ import summarize
import time

def keynote_generation(keynotes, text):
    llm = OllamaLLM(model="llama3.2")

    generated_keynotes = []

    keynote_prompt = """
    As a knowledgeable teacher, your task is to create a concise yet comprehensive reviewer for students based on the topic provided. Structure the reviewer as follows:
    Overview: A brief summary (1-2 sentences).
    Key Terms: Essential terms with short definitions.
    Questions: 3 exam-style questions.
    Tips: 1-2 practical tips for understanding.
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
