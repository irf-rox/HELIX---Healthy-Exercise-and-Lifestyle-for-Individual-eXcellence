import os
import shutil
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import psutil

PARENT_FOLDER_ID = "188eYmPiSfbEaRA8rpZBlTWNYIGjppLXX"
SERVICE_ACCOUNT_FILE = 'Helix/helix-446516-ca5f66874e2b.json'

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return credentials

def get_drive_folder_id(folder_name, parent_folder_id):
    credentials = authenticate()
    service = build('drive', 'v3', credentials=credentials)
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    return None

def download_chroma_from_drive(parent_folder_id):
    local_folder_name = 'temp_chroma/chroma'
    credentials = authenticate()
    service = build('drive', 'v3', credentials=credentials)

    os.makedirs(local_folder_name, exist_ok=True)

    chroma_folder_id = get_drive_folder_id('chroma', parent_folder_id)
    if chroma_folder_id is None:
        print("Error: 'chroma' folder not found in Google Drive.")
        return

    results = service.files().list(q=f"'{chroma_folder_id}' in parents", spaces='drive', fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    
    if not files:
        print("No files found in the chroma folder.")
        return

    for file in files:
        file_id = file['id']
        file_name = file['name']
        mime_type = file['mimeType']
        
        if mime_type == 'application/vnd.google-apps.folder':
            folder_path = os.path.join(local_folder_name, file_name)
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created folder: {folder_path}")
            download_chroma_from_drive_recursive(service, file_id, folder_path)
        else:
            file_path = os.path.join(local_folder_name, file_name)
            print(f"Downloading file: {file_name}")
            download_file(service, file_id, file_path)

    print("Chroma folder downloaded successfully.")

def download_file(service, file_id, file_path):
    """Downloads a single file from Google Drive."""
    request = service.files().get_media(fileId=file_id)
    with open(file_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {file_path}: {int(status.progress() * 100)}%.")

def download_chroma_from_drive_recursive(service, folder_id, local_folder):
    results = service.files().list(q=f"'{folder_id}' in parents", spaces='drive', fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    
    for file in files:
        file_id = file['id']
        file_name = file['name']
        mime_type = file['mimeType']
        
        if mime_type == 'application/vnd.google-apps.folder':
            folder_path = os.path.join(local_folder, file_name)
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created subfolder: {folder_path}")
            download_chroma_from_drive_recursive(service, file_id, folder_path)
        else:
            file_path = os.path.join(local_folder, file_name)
            print(f"Downloading subfolder file: {file_path}")
            download_file(service, file_id, file_path)

#if __name__ == "__main__":
#    download_chroma_from_drive(PARENT_FOLDER_ID)
