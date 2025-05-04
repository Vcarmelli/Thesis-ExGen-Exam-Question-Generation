import os
from pdf2image import convert_from_path
from ..model.rag import loader, create_retriever
from ..schema import QuestionSet

UPLOAD_FOLDER = 'app/static/uploads'
THUMBNAIL_FOLDER = 'app/static/thumbnails'

# Generate thumbnails from PDF
def convert_file_to_thumbnail(file_path, start_page=0, end_page=1, size=(256, 256)):
    images = convert_from_path(file_path, dpi=180)
    end_page = min(end_page, len(images))

    if end_page <= start_page:
        print("No pages to convert.")
        return []

    for count, page in enumerate(images[start_page:end_page], start=start_page):
        print(f"Creating thumbnail for page: {count + 1}")
        page.thumbnail(size)
        thumbnail_file = os.path.join(THUMBNAIL_FOLDER, f'thumbnail_{count}.jpg')
        page.save(thumbnail_file, 'JPEG')

    return [f'thumbnail_{i}.jpg' for i in range(start_page, end_page)]


# Function to retrieve text from the given pages using the retriever on the RAG.py
def retrieve_text_from_pages(file_path, pages):
    # Use the retriever to get text based on the page numbers
    documents = loader(file_path)  # Load the document using your loader
    retriever = create_retriever(documents, pages)  # Pass pages to the retriever
    return retriever.get_text()  # Assuming retriever has a method to get text


def retrieve_question_sets():
    """Get all question sets from the database"""
    try:
        question_sets = QuestionSet.query.all()
        sets_data = [{'id': qs.id, 'title': qs.title} for qs in question_sets]
        return sets_data
    except Exception as e:
        print(f"Error retrieving question sets: {e}")
        return []

# Function to convert range to list of pages
def parse_pages(pages_input):
    pages = set()
    page_ranges = pages_input.split(',')
    print("Page ranges:", page_ranges)
    for range_str in page_ranges:
        range_str = range_str.strip()
        if '-' in range_str:
            start, end = map(int, range_str.split('-'))
            pages.update(range(start, end + 1))
        elif range_str.isdigit():
            pages.add(int(range_str))
    return sorted(pages)

# Helper function to get the abbreviated question type
def exam_abbreviate(q_type):
    print("exam_abbreviate called with:", q_type) 
    return {
        'identification': 'IDN',
        'multiple_choice': 'MCQ',
        'true_false': 'TOF',
        'situation_based_questions': 'SBQ',
        'essay': 'ESS',
        'short_answer': 'SHA',
    }.get(q_type.lower(), 'TOF')  # default true or false


def get_bloom_level(bloom):
    return {
        'remember': 'Level 1: Remember',
        'understand': 'Level 2: Understand',
        'apply': 'Level 3: Apply',
        'analyze': 'Level 4: Analyze',
        'evaluate': 'Level 5: Evaluate',
        'create': 'Level 6: Create'
    }.get(bloom.lower(), 'Level 1: Remember') 


# save selected pages content in a txt file
def save_text(text):
    with open(os.path.join(UPLOAD_FOLDER, 'file.txt'), 'w') as file:
        file.write(text)
    print("Text saved to app/static/uploads/file.txt")


def retrieve_text():
    file_path = os.path.join(UPLOAD_FOLDER, 'file.txt')
    if not os.path.exists(file_path):
        return False

    with open(file_path, 'r') as file:
        content = file.read().strip()

    print(f"Text retrieved from app/static/uploads/file.txt: {len(content)} characters")
    return content if content else False