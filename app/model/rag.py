# File Loader and Splitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

# Data Embedding and Storage
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import logging


############################################ Load and Split Document ############################################

def loader(file_path): # Load the document
    loader = PyPDFLoader(file_path=file_path)
    documents = loader.load()

    return documents

def split_documents(documents: list[Document]): # Split the document
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300,

    )
    chunks = text_splitter.split_documents(documents)
    return chunks

############################################ Data Embedding and Storage ############################################


def get_embedding_function():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings

def get_chroma(chunks):
    persist_directory = "app/chroma_db"
    embedding_function = get_embedding_function()  # Initialize the embedding function
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        collection_name="my_collection",
        persist_directory=persist_directory,  # Ensure this is provided
    )

    logging.info("Vector database created.")
    print("Chunks successfully stored in ChromaDB.")
    return vector_db



########################################### Retrieve the vector database ###########################################

def create_retriever(vector_db, query):
    pass
    