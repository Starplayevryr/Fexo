import os
from pathlib import Path
from .keywords import contains_financial_keywords
from .pdf_utils import is_scanned_heuristic

# Try importing OpenAI LLM
try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None

# Try importing Google Gemini LLM
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from google.api_core.exceptions import ResourceExhausted
except Exception:
    ChatGoogleGenerativeAI = None
    ResourceExhausted = None

# Try importing LlamaParse
try:
    from llama_parse import LlamaParse
except Exception:
    LlamaParse = None


# Do not keep a global parser instance; initialize per-call to avoid event loop reuse issues
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

# Check if API keys or parser are available for a provider
def have_keys_for(provider: str) -> bool:
    if provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    if provider == "google":
        return bool(os.getenv("GOOGLE_API_KEY"))
    if provider == "llama":
        return bool(LLAMA_CLOUD_API_KEY and LlamaParse)
    return False

# Build prompt for table detection
def make_prompt_for_table_detection(sample_text: str) -> str:
    return (
        "You are an assistant that identifies tables in documents.\n"
        "Return JSON list like:\n"
        "[{\"title\": \"<table title>\", \"page_hint\": <page>, \"keywords\": [\"...\"], \"confidence\": 0-1}]\n"
        f"Document snippet:\n---\n{sample_text}\n---"
    )

# Main router to select and call the appropriate LLM provider
def route_llm(pages: int, sample_text: str, is_scanned: bool, file_path: Path = None):
    """
    Route to the appropriate LLM:
    Priority:
    1. LlamaParse
    2. Gemini (Google)
    3. OpenAI
    4. Stub fallback
    """
    # --- Determine provider & model ---
    if LLAMA_CLOUD_API_KEY and LlamaParse and file_path:
        provider, model = "llama", "llama-parse"
    elif pages > 10 or is_scanned:
        provider, model = "google", "gemini-1.5-pro"
    elif contains_financial_keywords(sample_text):
        provider, model = "openai", "gpt-4o"
    else:
        provider, model = "openai", "gpt-4o-mini"

    # --- Check if API key / parser exists ---
    if not have_keys_for(provider):
        print(f"Missing API key for {provider}, using stub.")
        return stub_llm(provider, model)

    # --- 1. LlamaParse ---
    if provider == "llama" and LLAMA_CLOUD_API_KEY and LlamaParse and file_path:
        def call_llama(_prompt=None):
            try:
                # Initialize a fresh parser per request to avoid closed-loop issues
                parser = LlamaParse(api_key=LLAMA_CLOUD_API_KEY, result_type="markdown")
                result = parser.load_data(str(file_path))

                tables = []
                for r in result:
                    if hasattr(r, "text") and "|" in r.text:  # crude markdown table check
                        tables.append({
                            "title": "Detected Table",
                            "content": r.text.split("\n"),
                            "page_hint": getattr(r, "page", None),
                        })
                return {
                    "provider": "LlamaParse",
                    "model": "llama-parse",
                    "pages": pages,
                    "table_count": len(tables),
                    "tables": tables,
                }
            except Exception as e:
                print(f"⚠️ LlamaParse failed: {e}, using stub.")
                return stub_llm(provider, model)(_prompt)
        return call_llama

    # --- 2. OpenAI ---
    if provider == "openai" and ChatOpenAI:
        llm = ChatOpenAI(model=model)
        def call_openai(prompt):
            try:
                return {
                    "provider": "openai",
                    "model": model,
                    "output": str(llm.invoke(prompt).content)
                }
            except Exception as e:
                print(f"OpenAI LLM failed: {e}, using stub.")
                return stub_llm(provider, model)(prompt)
        return call_openai

    # --- 3. Gemini (Google) ---
    if provider == "google" and ChatGoogleGenerativeAI:
        llm = ChatGoogleGenerativeAI(model=model)
        def call_gemini(prompt):
            try:
                return {
                    "provider": "google",
                    "model": model,
                    "output": str(llm.invoke(prompt).content)
                }
            except Exception as e:
                print(f"Gemini LLM failed: {e}, using stub.")
                return stub_llm(provider, model)(prompt)
        return call_gemini

    # --- 4. Stub fallback ---
    return stub_llm(provider, model)

# Stub LLM for fallback when real provider is unavailable
def stub_llm(provider, model):
    """Return a dummy stub LLM response."""
    def _stub(_prompt=None):
        return {
            "provider": f"{provider} (stub)",
            "model": model,
            "tables": [{"title": "Stub Table", "content": ["row1 col1 col2", "row2 col1 col2"], "page_hint": None}],
            "table_count": 1,
        }
    return _stub

# Detect if PDF is likely scanned (image-based)
def detect_if_scanned(file_path: Path, min_text_threshold: int = 20, empty_ratio: float = 0.7):
    """Detect if PDF is likely scanned (image-based)"""
    try:
        import fitz
        with fitz.open(file_path) as doc:
            page_count = len(doc)
            empty_pages = 0
            for page in doc:
                text = page.get_text()
                if len(text.strip()) < min_text_threshold:
                    empty_pages += 1
            return (empty_pages / page_count) >= empty_ratio, page_count
    except Exception:
        return False, 0
