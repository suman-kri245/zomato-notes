
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend import models
from backend import schemas


# ============================================================
# USER FUNCTIONS
# ============================================================

def create_user(
    db: Session,
    user: schemas.UserCreate,
):
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# ============================================================
# NOTE FUNCTIONS - CREATE
# ============================================================

def create_note(
    db: Session,
    note: schemas.NoteCreate,
):
    # Check owner before creating note
    owner = (
        db.query(models.User)
        .filter(models.User.id == note.owner_id)
        .first()
    )

    if owner is None:
        return None

    db_note = models.Note(
        title=note.title,
        content=note.content,
        tag=note.tag,
        owner_id=note.owner_id,
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note


# ============================================================
# NOTE FUNCTIONS - GET ALL
# ============================================================

def get_all_notes(
    db: Session,
    tag: str = None,
):
    query = db.query(models.Note)

    if tag:
        query = query.filter(
            models.Note.tag == tag
        )

    return query.all()


# ============================================================
# NOTE FUNCTIONS - GET ONE
# ============================================================

def get_note_by_id(
    db: Session,
    note_id: int,
):
    return (
        db.query(models.Note)
        .filter(models.Note.id == note_id)
        .first()
    )


# ============================================================
# NOTE FUNCTIONS - UPDATE
# ============================================================

def update_note(
    db: Session,
    note_id: int,
    note: schemas.NoteCreate,
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
    db_note.tag = note.tag

    db.commit()
    db.refresh(db_note)

    return db_note


# ============================================================
# NOTE FUNCTIONS - DELETE
# ============================================================

def delete_note(
    db: Session,
    note_id: int,
):
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


# ============================================================
# SEARCH DATA
# ============================================================

def get_notes_for_search(
    db: Session,
):
    notes = (
        db.query(models.Note)
        .all()
    )

    return [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "owner_id": note.owner_id,
            "created_at": note.created_at,
        }
        for note in notes
    ]


# ============================================================
# BULK IMPORT
# ============================================================

def import_notes(
    db: Session,
    owner_id: int,
    lines: list[str],
):
    # Validate owner BEFORE creating any note
    owner = (
        db.query(models.User)
        .filter(models.User.id == owner_id)
        .first()
    )

    if owner is None:
        return None

    notes = []

    for line in lines:
        db_note = models.Note(
            title=line[:120],
            content=line,
            tag="general",
            owner_id=owner_id,
        )

        db.add(db_note)
        notes.append(db_note)

    db.commit()

    for note in notes:
        db.refresh(note)

    return notes


# ============================================================
# REPORT - TAG SUMMARY
# Raw SQL + GROUP BY + HAVING
# ============================================================

def get_tag_summary(
    db: Session,
):
    query = text(
        """
        SELECT
            tag,
            COUNT(*) AS note_count
        FROM notes
        WHERE tag IS NOT NULL
        GROUP BY tag
        HAVING COUNT(*) > 1
        ORDER BY note_count DESC
        """
    )

    result = db.execute(query)

    return [
        {
            "tag": row.tag,
            "note_count": row.note_count,
        }
        for row in result
    ]


# ============================================================
# REPORT - LONG NOTES
# Raw SQL + SUBQUERY
# ============================================================

def get_long_notes(
    db: Session,
):
    query = text(
        """
        SELECT
            id,
            title,
            content,
            tag,
            owner_id,
            created_at
        FROM notes
        WHERE LENGTH(content) > (
            SELECT AVG(LENGTH(content))
            FROM notes
        )
        ORDER BY id
        """
    )

    result = db.execute(query)

    return [
        {
            "id": row.id,
            "title": row.title,
            "content": row.content,
            "tag": row.tag,
            "owner_id": row.owner_id,
            "created_at": row.created_at,
        }
        for row in result
    ]


# ============================================================
# REPORT - USER NOTES
# Raw SQL + JOIN
# ============================================================

def get_user_notes_report(
    db: Session,
):
    query = text(
        """
        SELECT
            users.id AS user_id,
            users.name AS user_name,
            users.email AS email,
            COUNT(notes.id) AS note_count
        FROM users
        LEFT JOIN notes
            ON users.id = notes.owner_id
        GROUP BY
            users.id,
            users.name,
            users.email
        ORDER BY users.id
        """
    )

    result = db.execute(query)

    return [
        {
            "user_id": row.user_id,
            "user_name": row.user_name,
            "email": row.email,
            "note_count": row.note_count,
        }
        for row in result
    ]
