from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import os
import shutil

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'Helix/helix-446516-badd75b8e1cc.json'
PARENT_FOLDER_ID = "188eYmPiSfbEaRA8rpZBlTWNYIGjppLXX"

CHROMA_PATH = "chroma"
DATA_PATH = "Dataset"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def authenticate():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return credentials

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
    return chunks

def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_texts(
        texts=texts,
        embedding=embedding_function,
        metadatas=metadatas,
        persist_directory=CHROMA_PATH,
    )
    db.persist()

def get_drive_folder_id(folder_name, parent_folder_id):
    credentials = authenticate()
    service = build('drive', 'v3', credentials=credentials)
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    return None

def delete_drive_folder(folder_id):
    credentials = authenticate()
    service = build('drive', 'v3', credentials=credentials)
    service.files().delete(fileId=folder_id).execute()

def upload_file_to_drive(file_path, parent_folder_id):
    credentials = authenticate()
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [parent_folder_id]
    }
    media = MediaFileUpload(file_path)
    service.files().create(body=file_metadata, media_body=media).execute()

def upload_chroma_to_drive(local_chroma_path, drive_parent_folder_id):
    credentials = authenticate()
    service = build('drive', 'v3', credentials=credentials)

    existing_chroma_id = get_drive_folder_id("chroma", drive_parent_folder_id)
    if existing_chroma_id:
        delete_drive_folder(existing_chroma_id)

    folder_metadata = {
        'name': 'chroma',
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [drive_parent_folder_id]
    }
    chroma_folder = service.files().create(body=folder_metadata, fields="id").execute()
    chroma_folder_id = chroma_folder['id']

    for item in os.listdir(local_chroma_path):
        item_path = os.path.join(local_chroma_path, item)
        if os.path.isdir(item_path):
            subfolder_metadata = {
                'name': item,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [chroma_folder_id]
            }
            subfolder = service.files().create(body=subfolder_metadata, fields="id").execute()
            subfolder_id = subfolder['id']

            for sub_item in os.listdir(item_path):
                sub_item_path = os.path.join(item_path, sub_item)
                upload_file_to_drive(sub_item_path, subfolder_id)
        else:
            upload_file_to_drive(item_path, chroma_folder_id)

if __name__ == "__main__":
    generate_data_store()
    upload_chroma_to_drive(CHROMA_PATH, PARENT_FOLDER_ID)
    print("Created folder in Google Drive.")
