import requests
from bs4 import BeautifulSoup
import re

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