from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(path):
    text_parts = []
    with open(path, "rb") as fh:
        reader = PdfReader(fh)
        for page in reader.pages:
            try:
                t = page.extract_text()
            except Exception:
                t = ""
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)

def extract_text_from_docx(path):
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paragraphs)