from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Header,
    BackgroundTasks,
    UploadFile,
    File,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import asyncio
import time

import crud
import models
import schemas
import algorithms
import semantic_search

from database import engine, get_db


# ============================================================
# DATABASE
# ============================================================

models.Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Zomato Notes API"
)


# ============================================================
# CORS
# ============================================================

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PROCESS TIME MIDDLEWARE
# ============================================================

@app.middleware("http")
async def add_process_time(request, call_next):

    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)

    return response


# ============================================================
# TOKEN AUTHENTICATION
# ============================================================

SECRET_TOKEN = "zomato-secret-token"


def verify_token(
    x_token: str = Header(...)
):
    if x_token != SECRET_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    return x_token


# ============================================================
# BACKGROUND TASK
# ============================================================

async def index_note():

    await asyncio.sleep(2)

    print("Note indexed successfully.")


# ============================================================
# CREATE USER
# ============================================================

@app.post(
    "/users",
    response_model=schemas.UserResponse
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    return crud.create_user(db, user)


# ============================================================
# CREATE NOTE
# ============================================================

@app.post(
    "/notes",
    response_model=schemas.NoteResponse
)
def create_note(
    note: schemas.NoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    db_note = crud.create_note(
        db,
        note
    )

    if db_note is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found"
        )

    background_tasks.add_task(index_note)

    return db_note


# ============================================================
# GET ALL NOTES
# ============================================================

@app.get(
    "/notes",
    response_model=list[schemas.NoteResponse]
)
def get_notes(
    tag: str = None,
    db: Session = Depends(get_db)
):

    return crud.get_all_notes(
        db,
        tag
    )


# ============================================================
# PART 2 - KEYWORD SEARCH
# IMPORTANT:
# THIS MUST COME BEFORE /notes/{note_id}
# ============================================================

@app.get("/notes/search")
def search_notes(
    keyword: str = None,
    sort_by: str = None,
    db: Session = Depends(get_db)
):

    notes = crud.get_notes_for_search(db)

    # --------------------------------------------------------
    # RELEVANCE SEARCH
    # --------------------------------------------------------

    if keyword:

        keyword = keyword.strip().lower()

        for note in notes:

            content = note.get(
                "content",
                ""
            ).lower()

            note["score"] = content.count(
                keyword
            )

        result = algorithms.insertion_sort_by_key(
            notes,
            key="score"
        )

        return result[:5]

    # --------------------------------------------------------
    # DATE SORT
    # --------------------------------------------------------

    if sort_by == "date":

        for note in notes:

            created_at = note.get(
                "created_at"
            )

            if created_at:
                note["created_at_epoch"] = (
                    created_at.timestamp()
                )
            else:
                note["created_at_epoch"] = 0

        return algorithms.insertion_sort_by_key(
            notes,
            key="created_at_epoch"
        )

    return notes


# ============================================================
# PART 2 - EXACT TITLE LOOKUP
# ============================================================

@app.get("/notes/lookup")
def lookup_notes(
    title: str,
    algo: str = "iterative",
    db: Session = Depends(get_db)
):

    notes = crud.get_notes_for_search(db)

    if not notes:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    # --------------------------------------------------------
    # CREATE TITLE LIST
    # --------------------------------------------------------

    titles = []

    for note in notes:
        titles.append(
            note["title"]
        )

    # --------------------------------------------------------
    # MANUAL ALPHABETICAL INSERTION SORT
    # --------------------------------------------------------

    for i in range(
        1,
        len(titles)
    ):

        current = titles[i]

        j = i - 1

        while (
            j >= 0
            and titles[j].lower()
            > current.lower()
        ):

            titles[j + 1] = titles[j]

            j -= 1

        titles[j + 1] = current

    # --------------------------------------------------------
    # SELECT SEARCH ALGORITHM
    # --------------------------------------------------------

    if algo == "recursive":

        index = algorithms.binary_search_recursive(
            titles,
            title,
            0,
            len(titles) - 1
        )

    else:

        index = algorithms.binary_search_iterative(
            titles,
            title
        )

    # --------------------------------------------------------
    # NOT FOUND
    # --------------------------------------------------------

    if index == -1:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    # --------------------------------------------------------
    # RETURN NOTE
    # --------------------------------------------------------

    matched_title = titles[index].lower()

    for note in notes:

        if (
            note["title"].lower()
            == matched_title
        ):

            return note

    raise HTTPException(
        status_code=404,
        detail="Note not found"
    )


# ============================================================
# PART 2 - QUICK TAG FIND
# ============================================================

@app.get("/notes/quick-find")
def quick_find(
    tag: str,
    db: Session = Depends(get_db)
):

    notes = crud.get_notes_for_search(db)

    result = algorithms.linear_search(
        notes,
        key="tag",
        value=tag
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="No note found for this tag"
        )

    return result


# ============================================================
# PART 3 - SMART SEARCH
# ============================================================

@app.get("/notes/smart-search")
def smart_search(
    q: str,
    db: Session = Depends(get_db)
):

    notes = crud.get_notes_for_search(db)

    return semantic_search.semantic_search(
        q,
        notes
    )


# ============================================================
# GET SINGLE NOTE
#
# IMPORTANT:
# THIS ROUTE IS AFTER /notes/search
# /notes/lookup
# /notes/quick-find
# /notes/smart-search
# ============================================================

@app.get(
    "/notes/{note_id}",
    response_model=schemas.NoteResponse
)
def get_note(
    note_id: int,
    db: Session = Depends(get_db)
):

    note = crud.get_note_by_id(
        db,
        note_id
    )

    if note is None:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note


# ============================================================
# UPDATE NOTE
# ============================================================

@app.put(
    "/notes/{note_id}",
    response_model=schemas.NoteResponse
)
def update_note(
    note_id: int,
    note: schemas.NoteCreate,
    db: Session = Depends(get_db)
):

    updated_note = crud.update_note(
        db,
        note_id,
        note
    )

    if updated_note is None:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return updated_note


# ============================================================
# DELETE NOTE
# ============================================================

@app.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token)
):

    deleted_note = crud.delete_note(
        db,
        note_id
    )

    if deleted_note is None:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return {
        "message": "Note deleted successfully"
    }


# ============================================================
# BULK IMPORT NOTES
# ============================================================

@app.post("/notes/import")
async def import_notes(
    owner_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    # --------------------------------------------------------
    # ONLY TXT
    # --------------------------------------------------------

    if not file.filename.lower().endswith(
        ".txt"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only .txt files are allowed"
        )

    # --------------------------------------------------------
    # READ FILE
    # --------------------------------------------------------

    content = await file.read()

    if not content:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    # --------------------------------------------------------
    # DECODE
    # --------------------------------------------------------

    try:

        text = content.decode(
            "utf-8-sig"
        )

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded"
        )

    # --------------------------------------------------------
    # GET NON EMPTY LINES
    # --------------------------------------------------------

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:

        raise HTTPException(
            status_code=400,
            detail="No notes found in file"
        )

    # --------------------------------------------------------
    # IMPORT
    # --------------------------------------------------------

    notes = crud.import_notes(
        db,
        owner_id,
        lines
    )

    if notes is None:

        raise HTTPException(
            status_code=404,
            detail="Owner not found"
        )

    return {
        "message": (
            f"{len(notes)} "
            "notes imported successfully"
        )
    }


# ============================================================
# REPORT - TAG SUMMARY
# ============================================================

@app.get("/reports/tag-summary")
def tag_summary(
    db: Session = Depends(get_db)
):

    return crud.get_tag_summary(db)


# ============================================================
# REPORT - LONG NOTES
# ============================================================

@app.get("/reports/long-notes")
def long_notes(
    db: Session = Depends(get_db)
):

    return crud.get_long_notes(db)


# ============================================================
# REPORT - USER NOTES
# ============================================================

@app.get("/reports/user-notes")
def user_notes_report(
    db: Session = Depends(get_db)
):

    return crud.get_user_notes_report(db)


# ============================================================
# OLD TAG SEARCH - KEPT FOR COMPATIBILITY
# ============================================================

@app.get("/search/tag")
def search_by_tag(
    tag: str,
    db: Session = Depends(get_db)
):

    notes = crud.get_notes_for_search(db)

    return algorithms.linear_search_tag(
        notes,
        tag
    )


# ============================================================
# OLD TITLE SEARCH - KEPT FOR COMPATIBILITY
# ============================================================

@app.get("/search/title")
def search_by_title(
    title: str,
    db: Session = Depends(get_db)
):

    notes = crud.get_notes_for_search(db)

    sorted_notes = algorithms.insertion_sort(
        notes
    )

    result = algorithms.binary_search_title(
        sorted_notes,
        title
    )

    return result


# ============================================================
# OLD SMART SEARCH - KEPT FOR COMPATIBILITY
# ============================================================

@app.get("/smart-search")
def old_smart_search(
    query: str,
    db: Session = Depends(get_db)
):

    notes = crud.get_notes_for_search(db)

    return semantic_search.semantic_search(
        query,
        notes
    )


# ============================================================
# OLD TAG QUICK SEARCH - KEPT FOR COMPATIBILITY
# ============================================================

@app.get("/search/tag-quick")
def search_tag_quick(
    tag: str,
    db: Session = Depends(get_db)
):

    notes = crud.get_notes_for_search(db)

    # Manual insertion sort by tag
    sorted_notes = notes.copy()

    for i in range(
        1,
        len(sorted_notes)
    ):

        current = sorted_notes[i]

        j = i - 1

        while (
            j >= 0
            and sorted_notes[j]["tag"].lower()
            > current["tag"].lower()
        ):

            sorted_notes[j + 1] = sorted_notes[j]

            j -= 1

        sorted_notes[j + 1] = current

    return algorithms.binary_search_tag(
        sorted_notes,
        tag
    )