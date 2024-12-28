from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
#from langchain_community.vectorstores import Chroma
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import os
import shutil

CHROMA_PATH = "chroma"
DATA_PATH = "Dataset"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # Lightweight embedding model

def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    documents = loader.load()
    return documents

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks

def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    
    texts = [chunk.page_content for chunk in chunks] # Documents to text and metadata
    metadatas = [chunk.metadata for chunk in chunks]

    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_texts(
        texts=texts,
        embedding=embedding_function,
        metadatas=metadatas,
        persist_directory=CHROMA_PATH,
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

if __name__ == "__main__":
    generate_data_store()
