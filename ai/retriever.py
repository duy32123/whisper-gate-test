import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_PATH = BASE_DIR / "data" / "documents.json"

with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_accessible_documents(documents, player_state):
    unlocked_ids = set(player_state["documents_unlocked"])
    current_stage = player_state["stage"]
    return [
        doc for doc in documents
        if doc["id"] in unlocked_ids and doc["stage_required"] <= current_stage
    ]

def retrieve(query, player_state, k=3):
    accessible_documents = get_accessible_documents(documents, player_state)

    if not accessible_documents:
        return []

    doc_texts = [
        f"{doc['title']}. {doc['content']}"
        for doc in accessible_documents
    ]

    doc_embeddings = embedding_model.encode(
        doc_texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:k]

    results = []
    for idx in top_indices:
        doc = accessible_documents[idx]
        results.append({
            "id": doc["id"],
            "title": doc["title"],
            "content": doc["content"],
            "score": float(scores[idx])
        })

    return results