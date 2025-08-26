from pypdf import PdfReader

# Extracts text from the first few pages of a PDF, up to max_chars characters.
def extract_pdf_text(reader: PdfReader, max_chars: int = 1000) -> str:
    text_parts: list[str] = []
    for page in reader.pages[:5]:    # only first 5 pages
        try:
            t = page.extract_text() or ""   # Try to extract text from the page
        except Exception:                 # If extraction fails, use empty string
            t = ""
        if t:
            text_parts.append(t)          # Add extracted text if not empty
        joined = " ".join(text_parts).strip()     # Join all extracted text so far
        if len(joined) >= max_chars:
            return joined[:max_chars]           # Stop if max_chars reached
    return (" ".join(text_parts)).strip()[:max_chars]      # Return up to max_chars

# Heuristic to check if a PDF is likely scanned (very little text extracted)
def is_scanned_heuristic(sample_text: str) -> bool:
    return len(sample_text.strip()) < 50   # If text is very short, likely scanned
