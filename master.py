from googleapiclient.discovery import build
from google.oauth2 import service_account
from epub_parser import parse_epub
import io
from googleapiclient.http import MediaIoBaseDownload
import os
from concurrent.futures import ThreadPoolExecutor
import threading
from flask import Flask, jsonify

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "./epubmontinor-35b26bd8d1a6.json"

app = Flask(__name__)

def download_epub(service, item):
    """Download a single EPUB file if it doesn't already exist."""
    file_path = f"./{item['name']}"
    if os.path.exists(file_path):
        return  # Skip if the file already exists
    
    request = service.files().get_media(fileId=item["id"])
    with open(file_path, "wb") as file:
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    print(f"Downloaded: {item['name']}")

def download_epub_all(service, items):
    """Download all EPUB files concurrently."""
    with ThreadPoolExecutor() as executor:
        executor.map(lambda item: download_epub(service, item), items)

def get_epubs_list():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)
    results = (
        service.files()
        .list(q="mimeType='application/epub+zip'", fields="files(id, name)")
        .execute()
    )
    items = results.get("files", [])
    
    # Run download_epub_all in a separate thread to make it non-blocking
    download_thread = threading.Thread(target=download_epub_all, args=(service, items))
    download_thread.start()
    
    epubs_list = [{"id": item["id"], "name": item["name"]} for item in items]
    
    return epubs_list

@app.route("/epubs", methods=["GET"])
def list_epubs():
    """API endpoint to get the list of EPUB files."""
    return jsonify(get_epubs_list())

@app.route("/epub/<filename>", methods=["GET"])
def get_epub_chapters(filename):
    """API endpoint to get chapters of a specific EPUB file."""
    file_path = f"./{filename}"
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    # print(parse_epub(file_path))
    return jsonify(parse_epub(file_path))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
