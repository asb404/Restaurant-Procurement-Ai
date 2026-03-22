import re

import requests


def extract_text_from_pdf_url(pdf_url: str) -> str:
    try:
        import fitz  # type: ignore
    except Exception as error:
        raise ValueError("PyMuPDF (fitz) is required for PDF parsing") from error

    try:
        response = requests.get(pdf_url, timeout=20)
        response.raise_for_status()
    except Exception as error:
        raise ValueError(f"Failed to download PDF: {error}") from error

    try:
        document = fitz.open(stream=response.content, filetype="pdf")
        pages: list[str] = []
        for page in document:
            text = page.get_text("text") or ""
            pages.append(text)
        document.close()
    except Exception as error:
        raise ValueError(f"Failed to parse PDF: {error}") from error

    combined = "\n".join(pages)
    cleaned_lines = [re.sub(r"\s+", " ", line).strip() for line in combined.splitlines()]
    cleaned = "\n".join(line for line in cleaned_lines if line)

    if len(cleaned) > 50000:
        cleaned = cleaned[:50000]

    print("PDF parsed successfully")
    print(f"Extracted text length: {len(cleaned)}")

    return cleaned
