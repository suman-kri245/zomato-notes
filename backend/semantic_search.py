from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(notes):

    texts = []

    for note in notes:
        texts.append(note["content"])

    return model.encode(texts)


def semantic_search(query, notes):

    note_embeddings = create_embeddings(notes)

    query_embedding = model.encode([query])

    scores = cosine_similarity(
        query_embedding,
        note_embeddings
    )[0]

    ranked = []

    for note, score in zip(notes, scores):

        ranked.append({
            "note": note,
            "score": float(score)
        })

    ranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked[:5]
