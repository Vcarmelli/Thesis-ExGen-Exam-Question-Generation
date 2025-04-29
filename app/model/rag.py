# File Loader and Splitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

# Data Embedding and Storage
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import logging

# Retrieve the vector database
from langchain.prompts import PromptTemplate

############################################ Load and Split Document ############################################

def loader(file_path): # Load the document
    loader = PyPDFLoader(file_path=file_path)
    documents = loader.load()

    return documents

def split_documents(documents: list[Document]): 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Add source metadata to each chunk
    for chunk in chunks:
        chunk.metadata["source"] = chunk.metadata.get("source", "Unknown Source")
    
    return chunks


############################################ Data Embedding and Storage ############################################


def get_embedding_function():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings

def get_chroma(chunks):
    persist_directory = "app/chroma_db"
    embedding_function = get_embedding_function()  # Initialize the embedding function
    
    # Load existing Chroma database
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_function,
        collection_name="my_collection"
    )
    
    # Fetch existing metadata to check for duplicates
    existing_data = vector_db.get()
    existing_sources = {meta["source"] for meta in existing_data["metadatas"]}

    # Filter out duplicate chunks by checking their source
    new_chunks = [chunk for chunk in chunks if chunk.metadata["source"] not in existing_sources]

    if not new_chunks:
        print("No new documents to add. All chunks are already in the database.")
    else:
        # Add new chunks to the database
        vector_db.add_documents(documents=new_chunks)
        print(f"Added {len(new_chunks)} new chunks to the database.")
    
    logging.info("Vector database updated.")
    return vector_db




########################################### Retrieve the vector database ###########################################

def create_retriever(documents, pages):
    # Filter the documents based on the pages provided
    relevant_documents = [documents[page_num - 1] for page_num in pages if page_num <= len(documents)]
    
    # Assuming you want to combine the texts of the selected pages
    retrieved_text = " ".join([doc.page_content for doc in relevant_documents])

    # Return the retrieved text as a simple object or class
    return Retriever(retrieved_text)
    
class Retriever:
    def __init__(self, text):
        self.text = text

    def get_text(self):
        return self.text


def get_pages_from_vector_db():
    # Load the existing Chroma database
    vectordb = Chroma(
        persist_directory="app/chroma_db",
        embedding_function=get_embedding_function(),
        collection_name="my_collection"
    )
    
    # Fetch all stored data in the database
    data = vectordb.get()
    
    # Extract pages
    pages = set()  # Use a set to avoid duplicate pages
    for metadata in data["metadatas"]:
        page = metadata.get("page")  # Assuming 'page' is stored in the metadata
        if page is not None:
            pages.add(page)
    
    # Convert pages to a sorted list
    sorted_pages = sorted(pages)
    print(f"Pages stored in the database: {sorted_pages}")
    return sorted_pages


def get_documents_from_vector_db():
    # Load the existing Chroma database
    vectordb = Chroma(
        persist_directory="app/chroma_db",
        embedding_function=get_embedding_function(),
        collection_name="my_collection"
    )
    
    # Fetch all stored data in the database
    data = vectordb.get()
    
    # Extract documents with metadata
    documents = []  # List to store documents with associated metadata
    for index, metadata in enumerate(data["metadatas"]):
        content = data["documents"][index]  # Corresponding content
        documents.append({
            "page": metadata.get("page"),
            "source": metadata.get("source", "Unknown Source"),
            "content": content
        })
    
    # Print each document's details
    print("\nDocuments in the database:")
    # for doc in documents:
    #     print(f"Page: {doc['page']}")
    #     print(f"Source: {doc['source']}")
    #     print("Content Preview:")
    #     print(doc['content'][:500])  # Print the first 500 characters for brevity
    #     print("-" * 80)  # Separator for clarity)
    
    return documents


