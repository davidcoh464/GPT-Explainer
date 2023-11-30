from .pdf_parser import read_pdf
from .pptx_parser import read_pptx


def extract_text(path_to_file: str) -> list[str]:
    if path_to_file.endswith('.pptx'):
        return read_pptx(path_to_file)
    if path_to_file.endswith('.pdf'):
        return read_pdf(path_to_file)
    return []