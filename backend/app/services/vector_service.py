import faiss
import numpy as np


dimension = 384

index = faiss.IndexFlatL2(dimension)


def add_embedding(embedding):
    vector = np.array([embedding], dtype="float32")

    index.add(vector)


def search_embedding(embedding, k=3):
    vector = np.array([embedding], dtype="float32")

    distances, indices = index.search(vector, k)

    return distances, indices