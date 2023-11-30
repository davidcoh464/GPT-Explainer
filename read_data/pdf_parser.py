import PyPDF2


def read_pdf(path_to_pdf: str) -> list[str]:
    with open(path_to_pdf, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)
        pages_text = []
        for page_number in range(total_pages):
            page = pdf_reader.pages[page_number]
            pages_text.append(page.extract_text().strip())
        return pages_text
