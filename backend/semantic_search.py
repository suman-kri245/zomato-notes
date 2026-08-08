from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def note_to_text(note):
    title = str(note.get("title") or "")
    content = str(note.get("content") or "")
    tag = str(note.get("tag") or "")

    return f"{title} {content} {tag}".strip()


def semantic_search(query, notes, top_k=5):
    query = str(query or "").strip()

    if not query or not notes:
        return []

    valid_notes = []
    note_texts = []

    for note in notes:
        text = note_to_text(note)

        if text:
            valid_notes.append(note)
            note_texts.append(text)

    if not valid_notes:
        return []

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english"
    )

    try:
        note_embeddings = vectorizer.fit_transform(note_texts)
        query_embedding = vectorizer.transform([query])
    except ValueError:
        return []

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
