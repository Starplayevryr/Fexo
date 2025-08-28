import os
from pathlib import Path
from .keywords import contains_financial_keywords

# Try imports
try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None

try:
    from llama_parse import LlamaParse
except Exception:
    LlamaParse = None

LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")


def have_keys_for(provider: str) -> bool:
    if provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    if provider == "google":
        return bool(os.getenv("GOOGLE_API_KEY"))
    if provider == "llama":
        return bool(LLAMA_CLOUD_API_KEY and LlamaParse)
    return False


def make_prompt_for_table_detection(sample_text: str) -> str:
    return (
        "You are an assistant that identifies tables in documents along with the page number and title.\n"
        "Return JSON list like:\n"
        "[{\"title\": \"<table title>\", \"page_hint\": <page>, \"rows\": [[...]]}]\n"
        f"Document snippet:\n---\n{sample_text}\n---"
    )


def route_llm(pages, sample_text, is_scanned, file_path: Path = None):
    """
    Select and call appropriate LLM:
    Priority:
    1. LlamaParse (structured JSON)
    2. Gemini / OpenAI
    3. Stub fallback
    """

    # Determine provider
    if LLAMA_CLOUD_API_KEY and LlamaParse and file_path:
        provider, model = "llama", "llama-parse"
    elif len(pages) > 10 or is_scanned:
        provider, model = "google", "gemini-1.5-pro"
    elif contains_financial_keywords(sample_text):
        provider, model = "openai", "gpt-4o"
    else:
        provider, model = "openai", "gpt-4o-mini"

    if not have_keys_for(provider):
        print(f"⚠️ Missing API key for {provider}, using stub.")
        return stub_llm(provider, model)

    # ---------------- LlamaParse ----------------
    if provider == "llama":
        def run_llamaparse():
            parser = LlamaParse(api_key=LLAMA_CLOUD_API_KEY, result_type="markdown")
            result = parser.load_data(str(file_path))

            tables = []
            for r in result:
                if hasattr(r, "text") and "|" in r.text:
                    # Use nearest heading as title if available
                    heading = getattr(r, "heading", None) or getattr(getattr(r, "metadata", {}), "heading", None)
                    page_num = getattr(r, "page", None) or getattr(getattr(r, "metadata", {}), "page", None)
                    tables.append({
                        "title": heading or f"Table (Page {page_num})",
                        "page": page_num,
                        "rows": r.text.split("\n")
                    })
            return {
                "provider": "LlamaParse",
                "model": "llama-parse",
                "tables": tables
            }
        return {"func": run_llamaparse, "provider": provider, "model": model}

    # ---------------- OpenAI ----------------
    if provider == "openai" and ChatOpenAI:
        def run_openai():
            llm = ChatOpenAI(model=model)
            llm.invoke(make_prompt_for_table_detection(sample_text))
            return {"provider": "openai", "model": model, "tables": []}
        return {"func": run_openai, "provider": provider, "model": model}

    # ---------------- Gemini ----------------
    if provider == "google" and ChatGoogleGenerativeAI:
        def run_gemini():
            llm = ChatGoogleGenerativeAI(model=model)
            llm.invoke(make_prompt_for_table_detection(sample_text))
            return {"provider": "google", "model": model, "tables": []}
        return {"func": run_gemini, "provider": provider, "model": model}

    return stub_llm(provider, model)


def stub_llm(provider, model):
    def _stub(_prompt=None):
        return {
            "provider": f"{provider} (stub)",
            "model": model,
            "tables": [{
                "title": "Stub Table",
                "page": 1,
                "rows": ["row1 col1 col2", "row2 col1 col2"]
            }]
        }
    return {"func": _stub, "provider": provider, "model": model}
