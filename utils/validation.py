import os
from config import ALLOWED_EXTENSIONS


def is_allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


def validate_extracted_text(text: str) -> tuple[bool, str]:
    cleaned = text.strip()

    if not cleaned:
        return False, "The file was read, but no text could be extracted."

    if len(cleaned) < 200:
        return False, "The extracted text is too short to be a usable CV."

    return True, "Text extraction successful."