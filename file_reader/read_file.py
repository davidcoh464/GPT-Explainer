from file_reader import pdf_parser
from file_reader import pptx_parser


def extract_text(path_to_file: str) -> list[str]:
    if path_to_file.endswith('.pptx'):
        return pptx_parser.read_pptx(path_to_file)
    if path_to_file.endswith('.pdf'):
        return pdf_parser.read_pdf(path_to_file)
    return []
