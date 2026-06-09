"""Lightweight in-memory RAG for REMI.

Uses sentence-transformers (all-MiniLM-L6-v2) for embeddings.
~90MB model download on first run; cached afterwards.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

# Lazy-load encoder so the module imports quickly and the download only
# happens on first use (~90MB).
_encoder: SentenceTransformer | None = None


def _get_encoder() -> SentenceTransformer:
    global _encoder
    if _encoder is None:
        _encoder = SentenceTransformer("all-MiniLM-L6-v2")
    return _encoder


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks.

    Splits at paragraph boundaries (\n\n) when possible so that [Page N]
    and [Slide N] markers are kept intact inside each chunk.
    """
    chunks: list[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        if end < text_len:
            # Look for a paragraph break in the trailing overlap zone.
            search_start = max(start + chunk_size - overlap, start + 1)
            para_break = text.rfind("\n\n", search_start, end)
            if para_break != -1:
                end = para_break
            else:
                nl_break = text.rfind("\n", search_start, end)
                if nl_break != -1:
                    end = nl_break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        next_start = end - overlap
        if next_start <= start:
            break
        start = next_start

    return chunks


# Plain in-memory store chosen over ChromaDB because REMI targets small
# documents and a single Python dict + numpy keeps the stack minimal and
# avoids an extra dependency / persistent directory.
#   document_id -> [(chunk_text, normalized_embedding), ...]
VECTOR_STORE: dict[str, list[tuple[str, np.ndarray]]] = {}


def embed_chunks(document_id: str, chunks: list[str]) -> None:
    """Encode chunks, L2-normalize, and store them."""
    encoder = _get_encoder()
    embeddings = encoder.encode(chunks, convert_to_numpy=True)

    # L2-normalize so cosine similarity = dot product
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embeddings = embeddings / norms

    VECTOR_STORE[document_id] = [
        (chunk, emb) for chunk, emb in zip(chunks, embeddings)
    ]


def retrieve(document_id: str, query: str, k: int = 8) -> list[str]:
    """Embed the query and return the top-k most similar chunk texts."""
    if document_id not in VECTOR_STORE:
        return []

    encoder = _get_encoder()
    query_emb = encoder.encode([query], convert_to_numpy=True)[0]
    query_emb = query_emb / np.linalg.norm(query_emb)

    stored = VECTOR_STORE[document_id]
    chunks = [item[0] for item in stored]
    embeddings = np.array([item[1] for item in stored])

    similarities = np.dot(embeddings, query_emb)
    top_k_indices = np.argsort(similarities)[::-1][:k]

    return [chunks[i] for i in top_k_indices]
