import requests
from bs4 import BeautifulSoup
import re
import io
from pypdf import PdfReader
from pdf2image import convert_from_bytes
from urllib.parse import quote_plus, urljoin

def parse_letter_notes_from_url(url):
    # Fetch page with a common user-agent
    headers = {'User-Agent': 'leadzeppelin-bot/1.0 (+https://example.com)'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    # Collect candidate elements where notes/chords are often placed
    candidates = []
    candidates.extend([p.get_text(separator=' ', strip=True) for p in soup.find_all('p')])
    candidates.extend([pre.get_text(separator=' ', strip=True) for pre in soup.find_all('pre')])
    candidates.extend([code.get_text(separator=' ', strip=True) for code in soup.find_all('code')])
    # look for common classes/ids that might contain chords/notes
    for cls in ['chords', 'notes', 'song-notes', 'tab', 'verse', 'chorus']:
        for el in soup.find_all(class_=cls):
            candidates.append(el.get_text(separator=' ', strip=True))

    # Pattern to match tokens like C, D#, Eb, F#, G, A, B, and sequences separated by spaces or hyphens
    token_pattern = re.compile(r"\b[A-G](?:#|b)?\b", re.IGNORECASE)

    note_lines = []
    for text in candidates:
        if not text:
            continue
        # Normalize whitespace and strip surrounding punctuation
        line = re.sub(r'\s+', ' ', text).strip(' \t\n\r\f\v.,:;!()[]"')
        # find tokens matching musical note letters
        tokens = token_pattern.findall(line)
        if tokens:
            # If there are multiple tokens, consider this a note line
            if len(tokens) >= 1:
                # Preserve original token order and case-insensitive normalized to uppercase
                note_lines.append(tokens)

    # Convert tokens to a list-of-lists of uppercase notes
    parsed_notes = [[t.upper() for t in line] for line in note_lines]

    print("Matched note lines:", note_lines)
    return parsed_notes

def parse_notes_from_pdf_url(pdf_url):
    """
    Downloads a PDF from a URL and extracts raw text from its pages.
    This is suitable for PDFs where notes are stored as text.

    Args:
        pdf_url (str): The direct URL to the PDF file.

    Returns:
        list: A list of strings, where each string is the text of a page.
              Returns a list with an error message if it fails.
    """
    try:
        print(f"Downloading PDF from: {pdf_url}")
        # Download the PDF content into memory
        response = requests.get(pdf_url, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Create a file-like object from the binary content
        pdf_file = io.BytesIO(response.content)
        
        # Initialize the PDF reader
        reader = PdfReader(pdf_file)
        num_pages = len(reader.pages)
        print(f"PDF has {num_pages} page(s).")
        
        # Extract text from each page
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                print(f"Extracted text from page {i+1}.")
                # Clean up the text a bit
                clean_text = " ".join(text.split())
                extracted_pages.append(clean_text)
            else:
                print(f"No text found on page {i+1}.")
                
        if not extracted_pages:
            return ["Error: No text could be extracted from the PDF. It may be an image-based file."]

        return extracted_pages

    except requests.exceptions.RequestException as e:
        return [f"Error downloading PDF: {e}"]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [f"Error parsing PDF: {e}"]

def get_pdf_page_images_from_url(pdf_url, poppler_path=None):
    """
    Downloads a PDF from a URL and converts each page into an image.

    Args:
        pdf_url (str): The direct URL to the PDF file.
        poppler_path (str, optional): The path to the Poppler bin directory.
                                      Required for Windows if not in system PATH.

    Returns:
        list: A list of PIL Image objects, one for each page.
              Returns an error string in a list if it fails.
    """
    try:
        print(f"Downloading PDF for image conversion from: {pdf_url}")
        # Download the PDF content
        response = requests.get(pdf_url, timeout=15)
        response.raise_for_status()

        # Convert the PDF bytes into a list of images
        images = convert_from_bytes(response.content, poppler_path=poppler_path)
        
        print(f"Successfully converted {len(images)} page(s) to images.")
        return images

    except Exception as e:
        error_message = f"Failed to convert PDF to images: {e}. Ensure Poppler is installed and in your PATH."
        print(error_message)
        return [error_message]

def get_song_title_from_noobnotes_url(url):
    """
    Extracts a clean song title from a noobnotes.net URL.
    Example: 'https://noobnotes.net/cant-help-falling-in-love-elvis-presley/'
    Returns: 'Cant Help Falling In Love'
    """
    try:
        # Get the path part of the URL and remove slashes
        path = url.split('.net/')[1].strip('/')
        # Split by '-', capitalize, and remove artist name if present
        title_parts = path.split('-')
        
        # A simple heuristic: assume the last part might be the artist
        # and check if it's a common name or word. This is not perfect.
        common_words = ['elvis', 'presley', 'the', 'beatles', 'queen']
        if title_parts[-1].lower() in common_words:
            title_parts = title_parts[:-1]
        if title_parts[-1].lower() in common_words and len(title_parts) > 1:
             title_parts = title_parts[:-1]

        return ' '.join([part.capitalize() for part in title_parts])
    except Exception:
        return "Unknown Song Title"

def find_and_parse_pdf_from_makingmusicfun(song_title):
    """
    Searches makingmusicfun.net for a song, finds the corresponding PDF,
    and parses it.
    """
    try:
        # 1. Search for the song on makingmusicfun.net
        search_query = quote_plus(song_title) # URL-encode the title
        search_url = f"https://www.makingmusicfun.net/htm/search.php?q={search_query}"
        print(f"Searching at: {search_url}")

        headers = {'User-Agent': 'Mozilla/5.0'}
        search_response = requests.get(search_url, headers=headers)
        search_response.raise_for_status()
        soup = BeautifulSoup(search_response.content, 'html.parser')

        # 2. Find the first relevant link in the search results
        # This selector targets the first search result link
        result_link = soup.select_one('td.result-cell-title a')
        if not result_link or not result_link.has_attr('href'):
            return ["Error: Song not found on makingmusicfun.net."]
            
        song_page_url = urljoin("https://www.makingmusicfun.net/", result_link['href'])
        print(f"Found song page: {song_page_url}")

        # 3. Scrape the song page to find the PDF link
        song_page_response = requests.get(song_page_url, headers=headers)
        song_page_response.raise_for_status()
        song_soup = BeautifulSoup(song_page_response.content, 'html.parser')
        
        # PDF links are often in an `<a>` tag with text like "Print" or "Download"
        pdf_link_element = song_soup.find('a', title=lambda t: t and 'Print' in t)
        if not pdf_link_element or not pdf_link_element.has_attr('href'):
            return ["Error: PDF download link not found on the song page."]

        pdf_url = urljoin(song_page_url, pdf_link_element['href'])
        print(f"Found PDF URL: {pdf_url}")
        
        # 4. Use your existing PDF parsing function to get the text
        return parse_notes_from_pdf_url(pdf_url)

    except requests.exceptions.RequestException as e:
        return [f"Error accessing makingmusicfun.net: {e}"]
    except Exception as e:
        return [f"An unexpected error occurred during scraping: {e}"]