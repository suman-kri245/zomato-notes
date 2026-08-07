from sqlalchemy.orm import Session
from sqlalchemy import func, text

import models
import schemas
import ai_service


# =========================
# USER FUNCTIONS
# =========================

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# =========================
# NOTE CREATE
# =========================

def create_note(db: Session, note: schemas.NoteCreate):

    owner = (
        db.query(models.User)
        .filter(models.User.id == note.owner_id)
        .first()
    )

    if owner is None:
        return None

    # AI automatically generates tag
    ai_tag = ai_service.get_ai_response(
        note.title,
        note.content
    )

    db_note = models.Note(
        title=note.title,
        content=note.content,
        tag=ai_tag,
        owner_id=note.owner_id
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note


# =========================
# GET ALL NOTES
# =========================

def get_all_notes(db: Session, tag: str = None):

    query = db.query(models.Note)

    if tag:
        query = query.filter(
            models.Note.tag == tag
        )

    return query.all()


# =========================
# GET NOTE BY ID
# =========================

def get_note_by_id(db: Session, note_id: int):

    return (
        db.query(models.Note)
        .filter(models.Note.id == note_id)
        .first()
    )


# =========================
# UPDATE NOTE
# =========================

def update_note(
    db: Session,
    note_id: int,
    note: schemas.NoteCreate
):

    db_note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id)
        .first()
    )

    if db_note is None:
        return None

    db_note.title = note.title
    db_note.content = note.content

    # Generate new AI tag after update
    db_note.tag = ai_service.get_ai_response(
        note.title,
        note.content
    )

    db_note.owner_id = note.owner_id

    db.commit()
    db.refresh(db_note)

    return db_note


# =========================
# DELETE NOTE
# =========================

def delete_note(db: Session, note_id: int):

    db_note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id)
        .first()
    )

    if db_note is None:
        return None

    db.delete(db_note)
    db.commit()

    return db_note


# =========================
# IMPORT NOTES
# =========================

def import_notes(
    db: Session,
    owner_id: int,
    lines: list
):
    owner = (
        db.query(models.User)
        .filter(models.User.id == owner_id)
        .first()
    )

    if owner is None:
        return None

    notes = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        parts = [part.strip() for part in line.split("|")]

        title = parts[0]

        if len(parts) >= 2:
            content = parts[1]
        else:
            content = ""

        if len(parts) >= 3 and parts[2]:
            tag = parts[2]
        else:
            tag = "general"

        db_note = models.Note(
            title=title,
            content=content,
            tag=tag,
            owner_id=owner_id
        )

        db.add(db_note)
        notes.append(db_note)

    db.commit()

    for note in notes:
        db.refresh(note)

    return notes



# =========================
# REPORT: TAG SUMMARY
# =========================

def get_tag_summary(db: Session):

    query = text("""
        SELECT
            tag,
            COUNT(*) AS count
        FROM notes
        GROUP BY tag
        ORDER BY count DESC
    """)

    result = db.execute(query)

    return [
        {
            "tag": row.tag,
            "count": row.count
        }
        for row in result
    ]


# =========================
# REPORT: LONG NOTES
# =========================

def get_long_notes(db: Session):

    query = text("""
        SELECT
            id,
            title,
            content,
            tag,
            owner_id
        FROM notes
        WHERE LENGTH(content) > 200
        ORDER BY LENGTH(content) DESC
    """)

    result = db.execute(query)

    return [
        {
            "id": row.id,
            "title": row.title,
            "content": row.content,
            "tag": row.tag,
            "owner_id": row.owner_id
        }
        for row in result
    ]


# =========================
# REPORT: USER NOTES
# =========================

def get_user_notes_report(db: Session):

    query = text("""
        SELECT
            users.id AS user_id,
            users.name AS user_name,
            COUNT(notes.id) AS note_count
        FROM users
        LEFT JOIN notes
            ON users.id = notes.owner_id
        GROUP BY users.id, users.name
        ORDER BY note_count DESC
    """)

    result = db.execute(query)

    return [
        {
            "user_id": row.user_id,
            "user_name": row.user_name,
            "note_count": row.note_count
        }
        for row in result
    ]


# =========================
# SEARCH DATA
# =========================

def get_notes_for_search(db: Session):

    notes = (
        db.query(models.Note)
        .order_by(models.Note.id)
        .all()
    )

    return [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "owner_id": note.owner_id
        }
        for note in notes
    ]
