import io
from pypdf import PdfReader
from docx import Document


def parse_pdf(file_content: bytes) -> str:
    """Extract text from PDF file."""
    try:
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def parse_docx(file_content: bytes) -> str:
    """Extract text from DOCX file."""
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        return "\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {str(e)}")


def parse_document(file_content: bytes, filename: str) -> str:
    """Parse document based on file extension."""
    lower_filename = filename.lower()

    if lower_filename.endswith(".pdf"):
        return parse_pdf(file_content)
    elif lower_filename.endswith(".docx"):
        return parse_docx(file_content)
    elif lower_filename.endswith(".txt"):
        return file_content.decode("utf-8")
    else:
        raise ValueError(f"Unsupported file format: {filename}. Supported: PDF, DOCX, TXT")
