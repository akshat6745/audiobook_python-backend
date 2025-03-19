import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor

class chapterType:
    title: str
    text_chunks: list[str]

def parse_chapter(item_content):
    """Parses a single EPUB document item into a chapter dictionary."""
    soup = BeautifulSoup(item_content, "html.parser")

    # Extract chapter title (use first <h1> or <title> tag)
    title_tag = soup.find(["h1", "title"])
    title = title_tag.get_text(strip=True) if title_tag else "Untitled Chapter"

    # Extract text paragraphs from <p> tags
    text_chunks = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

    return {"title": title, "text_chunks": text_chunks} if text_chunks else None

def parse_epub(file_path):
    """Parses an EPUB file and returns structured chapters with paragraph-based text chunks."""
    book = epub.read_epub(file_path)
    items = [item.content for item in book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT]

    # Use multiprocessing to parse chapters in parallel
    with ProcessPoolExecutor() as executor:
        chapters = list(filter(None, executor.map(parse_chapter, items)))

    return chapters