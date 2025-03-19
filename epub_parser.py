import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

class chapterType:
   title: str
   text_chunks: list[str]

def parse_epub(file_path):
    """Parses an EPUB file and returns structured chapters with paragraph-based text chunks."""
    book = epub.read_epub(file_path)
    chapters: list[chapterType] = []

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.content, "html.parser")

            # Extract chapter title (use first <h1> or <title> tag)
            title_tag = soup.find(["h1", "title"])
            title = title_tag.get_text(strip=True) if title_tag else "Untitled Chapter"

            # Extract text paragraphs from <p> tags
            text_chunks = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

            # Append to chapters list if there are paragraphs
            if text_chunks:
                chapters.append({"title": title, "text_chunks": text_chunks})

    return chapters