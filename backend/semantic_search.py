# ============================================================
# ZOMATO NOTES - SEMANTIC SEARCH
# ============================================================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# LOAD SEMANTIC SEARCH MODEL
# ============================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

def create_embeddings(
    notes: list[dict],
):
    """
    Create embeddings from note content.
    """

    if not notes:
        return []

    texts = []

    for note in notes:
        content = note.get(
            "content",
            "",
        )

        texts.append(content)

    return model.encode(texts)


# ============================================================
# SEMANTIC SEARCH
# ============================================================

def semantic_search(
    query: str,
    notes: list[dict],
):
    """
    Search notes using semantic similarity.
    Returns the top 5 most relevant notes.
    """

    if not query or not query.strip():
        return []

    if not notes:
        return []

    query = query.strip()

    note_embeddings = create_embeddings(
        notes
    )

    query_embedding = model.encode(
        [query]
    )

    scores = cosine_similarity(
        query_embedding,
        note_embeddings,
    )[0]

    ranked = []

    for note, score in zip(
        notes,
        scores,
    ):
        ranked.append(
            {
                "note": note,
                "score": float(score),
            }
        )

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return ranked[:5]