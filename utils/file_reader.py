import os
from pypdf import PdfReader
from docx import Document


def extract_text_from_file(file_path: str) -> str:
    _, ext = os.path.splitext(file_path.lower())

    if ext == ".pdf":
        reader = PdfReader(file_path)
        pages_text = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)

        return "\n".join(pages_text)

    elif ext == ".docx":
        doc = Document(file_path)
        paragraphs = []

        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())

        return "\n".join(paragraphs)

    else:
        raise ValueError(f"Unsupported file type for extraction: {ext}")