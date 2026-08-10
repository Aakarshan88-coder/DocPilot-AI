from app.services.embedding_service import create_embedding
from app.services.vector_service import add_embedding, search_embedding


text = "DocPilot-AI is an AI document assistant."

embedding = create_embedding(text)

add_embedding(embedding)

distances, indices = search_embedding(embedding, k=1)

print("Distance:", distances)
print("Index:", indices)