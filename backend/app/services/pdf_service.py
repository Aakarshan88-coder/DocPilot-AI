from pypdf import PdfReader


def extract_pages_from_pdf(file_path: str):
    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        pages.append({
            "page_number": page_number,
            "text": page_text or "",
        })

    return pages


def extract_text_from_pdf(file_path: str):
    pages = extract_pages_from_pdf(file_path)

    return "\n".join(
        page["text"]
        for page in pages
        if page["text"]
    )