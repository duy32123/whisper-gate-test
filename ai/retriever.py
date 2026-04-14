import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

with open("data/documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

with open("state/player_state.json", "r", encoding="utf-8") as f:
    player_state = json.load(f)
    
def get_accessible_documents(documents, player_state):
    unlocked_ids = set(player_state["documents_unlocked"])
    current_stage = player_state["stage"]

    return [
        doc for doc in documents
        if doc["id"] in unlocked_ids and doc["stage_required"] <= current_stage
    ]

accessible_documents = get_accessible_documents(documents, player_state)
print("Accessible documents:")


embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

doc_texts = [doc["content"] for doc in accessible_documents]
doc_embeddings = embedding_model.encode(
    doc_texts,
    convert_to_numpy=True,
    normalize_embeddings=True
)

def retrieve(query, k=2):
    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    scores = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:k]

    results = []
    for idx in top_indices:
        results.append({
            "id": accessible_documents[idx]["id"],
            "title": accessible_documents[idx]["title"],
            "content": accessible_documents[idx]["content"],
            "score": float(scores[idx])
        })
    return results

if __name__ == "__main__":
    query = "Can the terminal logs be trusted?"
    results = retrieve(query, k=2)

    for item in results:
        print(item["title"], "-", item["score"])
        print(item["content"])
        print()