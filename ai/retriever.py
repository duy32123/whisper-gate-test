import importlib.util
import json
import math
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_PATH = BASE_DIR / "data" / "documents.json"

NVIDIA_EMBEDDING_MODEL = os.getenv("NVIDIA_EMBEDDING_MODEL", "baai/bge-m3")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)

_embedding_model = None
_nvidia_client = None


def _package_available(package: str) -> bool:
    return importlib.util.find_spec(package) is not None


def _nvidia_embeddings_available() -> bool:
    return bool(os.getenv("NVIDIA_API_KEY")) and _package_available("openai")


def _semantic_dependencies_available() -> bool:
    return all(
        _package_available(package)
        for package in ("sentence_transformers", "sklearn", "numpy")
    )


def _get_nvidia_client():
    global _nvidia_client
    if _nvidia_client is None:
        from openai import OpenAI

        _nvidia_client = OpenAI(
            api_key=os.environ["NVIDIA_API_KEY"],
            base_url=NVIDIA_BASE_URL,
        )
    return _nvidia_client


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer

        _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedding_model


def get_accessible_documents(documents, player_state):
    unlocked_ids = set(player_state["documents_unlocked"])
    current_stage = player_state["stage"]
    return [
        doc for doc in documents
        if doc["id"] in unlocked_ids and doc["stage_required"] <= current_stage
    ]


def _cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def _keyword_score(query: str, doc: dict) -> float:
    query_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    doc_terms = set(
        re.findall(
            r"[a-z0-9]+",
            f"{doc['title']} {doc['content']} {doc.get('type', '')}".lower(),
        )
    )

    if not query_terms:
        return 0.0

    return len(query_terms & doc_terms) / len(query_terms)


def _format_result(doc: dict, score: float) -> dict:
    return {
        "id": doc["id"],
        "title": doc["title"],
        "content": doc["content"],
        "score": float(score),
    }


def _keyword_retrieve(query: str, accessible_documents: list[dict], k: int):
    ranked_docs = sorted(
        accessible_documents,
        key=lambda doc: _keyword_score(query, doc),
        reverse=True,
    )

    return [
        _format_result(doc, _keyword_score(query, doc))
        for doc in ranked_docs[:k]
    ]


def _nvidia_retrieve(query: str, accessible_documents: list[dict], k: int):
    client = _get_nvidia_client()
    doc_texts = [
        f"{doc['title']}. {doc['content']}"
        for doc in accessible_documents
    ]
    embedding_inputs = [query, *doc_texts]

    response = client.embeddings.create(
        input=embedding_inputs,
        model=NVIDIA_EMBEDDING_MODEL,
        encoding_format="float",
        extra_body={"truncate": "NONE"},
    )

    embeddings = [item.embedding for item in response.data]
    query_embedding = embeddings[0]
    doc_embeddings = embeddings[1:]
    scored_docs = [
        (doc, _cosine_similarity(query_embedding, doc_embedding))
        for doc, doc_embedding in zip(accessible_documents, doc_embeddings)
    ]
    scored_docs.sort(key=lambda item: item[1], reverse=True)

    return [_format_result(doc, score) for doc, score in scored_docs[:k]]


def _local_semantic_retrieve(query: str, accessible_documents: list[dict], k: int):
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    embedding_model = _get_embedding_model()
    doc_texts = [
        f"{doc['title']}. {doc['content']}"
        for doc in accessible_documents
    ]

    doc_embeddings = embedding_model.encode(
        doc_texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    scores = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:k]

    return [
        _format_result(accessible_documents[idx], scores[idx])
        for idx in top_indices
    ]


def retrieve(query, player_state, k=3):
    accessible_documents = get_accessible_documents(documents, player_state)

    if not accessible_documents:
        return []

    if _nvidia_embeddings_available():
        return _nvidia_retrieve(query, accessible_documents, k)

    if _semantic_dependencies_available():
        return _local_semantic_retrieve(query, accessible_documents, k)

    return _keyword_retrieve(query, accessible_documents, k)
