from pypdf import PdfReader
import fitz  # PyMuPDF

def detect_if_scanned(file_path, min_text_threshold: int = 20, empty_ratio: float = 0.7):
    """
    Detect if a PDF is scanned (image-based) or text-based.

    Args:
        file_path: Path to the PDF file.
        min_text_threshold: Minimum characters per page to count as "non-empty".
        empty_ratio: Fraction of empty pages required to consider the PDF scanned.

    Returns:
        (is_scanned: bool, page_count: int, pages: list[str])
        - is_scanned: True if PDF has very little extractable text
        - page_count: total number of pages in PDF
        - pages: list of full text for each page
    """
    try:
        reader = PdfReader(str(file_path))
        pages = []
        empty_pages = 0

        for page in reader.pages:
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            text = text.strip()
            pages.append(text)

            if len(text) < min_text_threshold:
                empty_pages += 1

        is_scanned = empty_pages / max(len(pages), 1) >= empty_ratio
        page_count = len(pages)
        return is_scanned, page_count, pages  # return full page texts

    except Exception as e:
        print(f"[detect_if_scanned] PyPDF failed: {e}")

        # Fallback to PyMuPDF
        try:
            doc = fitz.open(str(file_path))
            pages = []
            empty_pages = 0

            for page in doc:
                text = page.get_text() or ""
                text = text.strip()
                pages.append(text)

                if len(text) < min_text_threshold:
                    empty_pages += 1

            is_scanned = empty_pages / max(len(pages), 1) >= empty_ratio
            page_count = len(pages)
            return is_scanned, page_count, pages

        except Exception as e2:
            print(f"[detect_if_scanned] Total failure: {e2}")
            return True, 0, []  # Assume scanned and return safe defaults
