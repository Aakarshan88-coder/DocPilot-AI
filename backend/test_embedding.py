from app.services.embedding_service import create_embedding

text = "DocPilot-AI is an AI document assistant."

embedding = create_embedding(text)

print("Embedding length:", len(embedding))
print("First 5 values:", embedding[:5])