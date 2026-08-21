import faiss
import numpy as np
import os
import pickle


dimension = 384

# =========================
# Persistent storage paths
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

VECTOR_STORE_DIR = os.path.join(
    BASE_DIR,
    "vector_store"
)

INDEX_PATH = os.path.join(
    VECTOR_STORE_DIR,
    "faiss.index"
)

METADATA_PATH = os.path.join(
    VECTOR_STORE_DIR,
    "metadata.pkl"
)


# =========================
# Create storage directory
# =========================

os.makedirs(
    VECTOR_STORE_DIR,
    exist_ok=True
)


# =========================
# Load existing data
# =========================

if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
else:
    index = faiss.IndexFlatL2(dimension)


if os.path.exists(METADATA_PATH):
    with open(METADATA_PATH, "rb") as file:
        metadata = pickle.load(file)
else:
    metadata = []


# =========================
# Save vector store
# =========================

def save_vector_store():

    faiss.write_index(
        index,
        INDEX_PATH
    )

    with open(
        METADATA_PATH,
        "wb"
    ) as file:

        pickle.dump(
            metadata,
            file
        )


# =========================
# Add embedding
# =========================

def add_embedding(
    embedding,
    document_id,
    user_id,
    chunk,
    page_number=None,
    chunk_index=None
):

    vector = np.array(
        [embedding],
        dtype="float32"
    )

    index.add(vector)

    metadata.append({
        "document_id": document_id,
        "user_id": user_id,
        "chunk": chunk,
        "page_number": page_number,
        "chunk_index": chunk_index,
    })

    save_vector_store()


# =========================
# Search similar
# =========================
def search_similar(
    embedding,
    user_id,
    document_id,
    top_k=3
):
    print("FAISS TOTAL VECTORS:", index.ntotal)
    print("METADATA COUNT:", len(metadata))
    print("SEARCH DOCUMENT ID:", document_id)

    if index.ntotal == 0:
        return []

    vector = np.array(
        [embedding],
        dtype="float32"
    )

    distances, indices = index.search(
        vector,
        min(index.ntotal, len(metadata))
    )

    results = []

    for distance, i in zip(distances[0], indices[0]):

        if i == -1:
            continue

        item = metadata[i]

        if (
            item["user_id"] == user_id
            and item["document_id"] == document_id
        ):
            results.append({
                **item,
                "distance": float(distance),
            })

            if len(results) == top_k:
                break

    return results



# =========================
# Delete document embeddings
# =========================

def delete_document_embeddings(
    document_id,
    user_id
):

    global index
    global metadata

    new_metadata = []
    vectors_to_keep = []

    for i, item in enumerate(metadata):

        if (
            item["document_id"] == document_id
            and item["user_id"] == user_id
        ):
            continue

        new_metadata.append(item)

        vector = index.reconstruct(i)

        vectors_to_keep.append(vector)

    if vectors_to_keep:

        new_index = faiss.IndexFlatL2(
            dimension
        )

        vectors = np.array(
            vectors_to_keep,
            dtype="float32"
        )

        new_index.add(vectors)

        index = new_index

    else:

        index = faiss.IndexFlatL2(
            dimension
        )

    metadata = new_metadata

    save_vector_store()