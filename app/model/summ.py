from transformers import pipeline

# summarizer = pipeline("summarization")
def summarize(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    return summarizer(text)[0]['summary_text']


# def generate_questions(text):
#     question_generator = pipeline(
#         "text-generation", 
#         model="google/pegasus-xsum", 
#         max_length=1000,)
#     return question_generator(text)