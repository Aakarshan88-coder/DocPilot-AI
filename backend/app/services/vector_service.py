import faiss
import numpy as np


dimension = 384

index = faiss.IndexFlatL2(dimension)

metadata = []


def add_embedding(
    embedding,
    document_id,
    user_id,
    chunk
):
    vector = np.array(
        [embedding],
        dtype="float32"
    )

    index.add(vector)

    metadata.append({
        "document_id": document_id,
        "user_id": user_id,
        "chunk": chunk
    })


def search_similar(
    embedding,
    user_id,
    document_id,
    top_k=3
):
    vector = np.array(
        [embedding],
        dtype="float32"
    )

    distances, indices = index.search(
        vector,
        top_k
    )

    results = []

    for i in indices[0]:

        if i == -1:
            continue

        item = metadata[i]

        if (
            item["user_id"] == user_id
            and item["document_id"] == document_id
        ):
            results.append(item)

    return results