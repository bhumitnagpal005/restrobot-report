import re

def clean_text(text: str) -> str:
    """
    Cleans raw text input:
    - converts to lowercase
    - strips leading/trailing whitespace
    - normalizes punctuation and multiple spaces
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower().strip()
    # Replace non-alphanumeric chars (except spaces & ₹) with space
    text = re.sub(r"[^\w\s₹.]", " ", text)
    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text
