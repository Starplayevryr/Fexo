# Checks if the input text contains any common financial keywords.
def contains_financial_keywords(text: str) -> bool:
    FIN_KWS = [
        "balance sheet", "cash flow", "profit and loss", "p&l",
        "income statement", "assets", "liabilities", "equity",
        "depreciation", "amortization", "ebitda", "revenue",
        "dividend", "operating profit", "financial statement"
    ]
    t = text.lower()
    return any(kw in t for kw in FIN_KWS)
