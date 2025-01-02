from transformers import pipeline

# summarizer = pipeline("summarization")
def summarize(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Split the text into chunks of 1064 characters
    chunk_size = 1064
    text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    # Summarize each chunk and combine the results
    summaries = []
    for chunk in text_chunks:
        summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
        summaries.append(summary)
        print(f"Summarized chunk: {summary}")
    
    # Combine all summaries into a single text
    return " ".join(summaries)

#simpler
# summarizer = pipeline("summarization")
# def summarize(text):
#     summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
#     return summarizer(text)[0]['summary_text']

# def generate_questions(text):
#     question_generator = pipeline(
#         "text-generation", 
#         model="google/pegasus-xsum", 
#         max_length=1000,)
#     return question_generator(text)