def create_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]
        chunks.append(chunk)

        start = end - overlap

    return chunks