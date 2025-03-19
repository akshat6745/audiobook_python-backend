from googleapiclient.discovery import build
from google.oauth2 import service_account
from epub_parser import parse_epub
import io
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "./epubmontinor-35b26bd8d1a6.json"


def list_epubs():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)

    results = (
        service.files()
        .list(
            q="mimeType='application/epub+zip'",  # Filter only EPUB files
            fields="files(id, name)",
        )
        .execute()
    )

    items = results.get("files", [])
    if not items:
        print("No EPUB files found.")
        return []
    print(items)
    # Get the first EPUB file
    first_epub = items[0]
    file_id = first_epub["id"]
    file_name = first_epub["name"]

    print(f"Downloading EPUB: {file_name} (ID: {file_id})")

    # Download the file
    request = service.files().get_media(fileId=file_id)
    file_path = f"./{file_name}"
    with open(file_path, "wb") as file:
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    print(f"Downloaded: {file_path}")

    # Parse the EPUB file and return chapters
    chapters = parse_epub(file_path)
    return chapters


if __name__ == "__main__":
    chapters_data = list_epubs()
    print(chapters_data)  # Print or process the returned chapters
