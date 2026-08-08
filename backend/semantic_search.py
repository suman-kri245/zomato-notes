
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# SEMANTIC SEARCH MODEL
# ============================================================

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ============================================================
# CONVERT NOTE TO TEXT
# ============================================================

def note_to_text(note):
    title = str(note.get("title") or "")
    content = str(note.get("content") or "")
    tag = str(note.get("tag") or "")

    return f"{title} {content} {tag}".strip()


# ============================================================
# SEMANTIC SEARCH
# ============================================================

def semantic_search(query, notes, top_k=5):

    query = str(query or "").strip()

    if not query:
        return []

    if not notes:
        return []

    note_texts = []
    valid_notes = []

    for note in notes:

        if not isinstance(note, dict):
            continue

        text = note_to_text(note)

        if not text:
            continue

        note_texts.append(text)
        valid_notes.append(note)

    if not valid_notes:
        return []

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    note_embeddings = model.encode(
        note_texts,
        convert_to_numpy=True
    )

    similarities = cosine_similarity(
        query_embedding,
        note_embeddings
    )[0]

    results = []

    for index, note in enumerate(valid_notes):

        result = note.copy()

        result["similarity_score"] = float(
            similarities[index]
        )

        results.append(result)

    results.sort(
        key=lambda item: item["similarity_score"],
        reverse=True
    )

    return results[:top_k]

