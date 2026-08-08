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
import json

from backend import crud
from backend import models
from backend import schemas
from backend import algorithms
from backend import semantic_search
from backend.ai_service import get_ai_response
from backend.database import engine, get_db


# ============================================================
# DATABASE
# ============================================================

models.Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(title="Zomato Notes API")


# ============================================================
# CORS
# ============================================================

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
# TOKEN AUTH
# ============================================================

SECRET_TOKEN = "zomato-secret-token"


def verify_token(x_token: str = Header(...)):
    if x_token != SECRET_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token",
        )


# ============================================================
# BACKGROUND TASK
# ============================================================

async def index_note():
    await asyncio.sleep(2)
    print("Note indexed successfully.")


# ============================================================
# USERS
# ============================================================

@app.post(
    "/users",
    response_model=schemas.UserResponse,
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    return crud.create_user(db, user)


# ============================================================
# NOTES - CREATE + AI SUGGESTION
# ============================================================

@app.post("/notes")
def create_note(
    note: schemas.NoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    db_note = crud.create_note(db, note)

    if db_note is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found",
        )

    ai_suggestion = None

    try:
        system_prompt = """
Instructions:
You are an AI assistant for an internal knowledge base.

Context:
The application stores engineering and incident notes.

Input:
Read the note content provided by the user.

Constraints:
- Return only a valid JSON object.
- The JSON object must contain exactly two keys:
  "tags" and "summary".
- "tags" must contain 1 to 3 short lowercase keyword strings.
- "summary" must be one sentence containing at most 20 words.
- No text may surround the JSON object.
- Do not use markdown code fences.

Output Format:
{
    "tags": ["keyword1", "keyword2"],
    "summary": "Short summary."
}
"""

        raw_response = get_ai_response(
            user_message=db_note.content,
            system_prompt=system_prompt,
        )

        parsed_response = json.loads(raw_response)

        if not isinstance(parsed_response, dict):
            raise ValueError(
                "AI response must be a JSON object"
            )

        if set(parsed_response.keys()) != {
            "tags",
            "summary",
        }:
            raise ValueError(
                "AI response must contain exactly tags and summary"
            )

        if not isinstance(
            parsed_response["tags"],
            list,
        ):
            raise ValueError(
                "AI tags must be a list"
            )

        if not isinstance(
            parsed_response["summary"],
            str,
        ):
            raise ValueError(
                "AI summary must be a string"
            )

        ai_suggestion = {
            "tags": parsed_response["tags"][:3],
            "summary": parsed_response["summary"],
        }

    except Exception as e:
        print("AI parsing error:", e)
        ai_suggestion = None

    background_tasks.add_task(index_note)

    return {
        "id": db_note.id,
        "title": db_note.title,
        "content": db_note.content,
        "tag": db_note.tag,
        "owner_id": db_note.owner_id,
        "created_at": db_note.created_at,
        "ai_suggestion": ai_suggestion,
    }


# ============================================================
# NOTES - LIST
# ============================================================

@app.get(
    "/notes",
    response_model=list[schemas.NoteResponse],
)
def get_notes(
    tag: str = None,
    db: Session = Depends(get_db),
):
    return crud.get_all_notes(db, tag)


# ============================================================
# PART 2 - RANKED SEARCH
# ============================================================

@app.get("/notes/search")
def ranked_search(
    keyword: str = None,
    sort_by: str = None,
    db: Session = Depends(get_db),
):
    notes = crud.get_notes_for_search(db)

    if keyword:
        keyword_lower = keyword.lower()

        for note in notes:
            content = note.get(
                "content",
                "",
            ).lower()

            note["score"] = content.count(
                keyword_lower
            )

        result = algorithms.insertion_sort_by_key(
            notes,
            key="score",
        )

        return result[:5]

    if sort_by == "date":

        for note in notes:

            created_at = note.get(
                "created_at"
            )

            if created_at is not None:
                try:
                    note["created_at_epoch"] = (
                        created_at.timestamp()
                    )
                except AttributeError:
                    note["created_at_epoch"] = 0
            else:
                note["created_at_epoch"] = 0

        result = algorithms.insertion_sort_by_key(
            notes,
            key="created_at_epoch",
        )

        return result

    return notes










































































































































































































@app.get("/notes/search")
def search_notes(
    keyword: str,
    db: Session = Depends(get_db),
):
    notes = crud.get_notes_for_search(db)

    keyword_lower = keyword.lower().strip()

    if not keyword_lower:
        return []

    results = []

    for note in notes:
        title = str(note.get("title", "")).lower()
        content = str(note.get("content", "")).lower()
        tag = str(note.get("tag", "") or "").lower()

        if (
            keyword_lower in title
            or keyword_lower in content
            or keyword_lower in tag
        ):
            results.append(note)

    return results
# ============================================================
# PART 2 - EXACT TITLE LOOKUP
# ============================================================

@app.get("/notes/lookup")
def lookup_note(
    title: str,
    algo: str = "iterative",
    db: Session = Depends(get_db),
):
    notes = crud.get_notes_for_search(db)

    sorted_notes = algorithms.insertion_sort(
        notes
    )

    titles = [
        note["title"]
        for note in sorted_notes
    ]

    if algo == "iterative":

        index = algorithms.binary_search_iterative(
            titles,
            title,
        )

    elif algo == "recursive":

        index = algorithms.binary_search_recursive(
            titles,
            title,
            0,
            len(titles) - 1,
        )

    else:

        raise HTTPException(
            status_code=400,
            detail="algo must be iterative or recursive",
        )

    if index == -1:
        return {
            "message": "Note not found",
        }

    return sorted_notes[index]


# ============================================================
# PART 2 - QUICK TAG FIND
# ============================================================

@app.get("/notes/quick-find")
def quick_find(
    tag: str,
    db: Session = Depends(get_db),
):
    notes = crud.get_notes_for_search(db)

    result = algorithms.linear_search(
        notes,
        key="tag",
        value=tag,
    )

    if result is None:
        return {
            "message": "No note found for this tag",
        }

    return result


# ============================================================
# PART 3 - SMART SEARCH
# ============================================================

@app.get("/notes/smart-search")
def smart_search(
    q: str,
    db: Session = Depends(get_db),
):
    notes = crud.get_notes_for_search(db)

    return semantic_search.semantic_search(
        q,
        notes,
    )


# ============================================================
# OLD SEARCH - TAG
# ============================================================

@app.get("/search/tag")
def search_bnotey_tag(
    tag: str,
    db: Session = Depends(get_db),
):
    notes = crud.get_notes_for_search(db)

    return algorithms.linear_search_tag(
        notes,
        tag,
    )


# ============================================================
# OLD SEARCH - TITLE
# ============================================================

@app.get("/search/title")
def search_by_title(
    title: str,
    db: Session = Depends(get_db),
):
    notes = crud.get_notes_for_search(db)

    sorted_notes = algorithms.insertion_sort(
        notes
    )

    return algorithms.binary_search_title(
        sorted_notes,
        title,
    )


# ============================================================
# OLD SEARCH - TAG QUICK
# ============================================================

@app.get("/search/tag-quick")
def search_tag_quick(
    tag: str,
    db: Session = Depends(get_db),
):
    notes = crud.get_notes_for_search(db)

    sorted_notes = algorithms.insertion_sort(
        notes
    )

    return algorithms.binary_search_tag(
        sorted_notes,
        tag,
    )


# ============================================================
# NOTES - SINGLE NOTE
# ============================================================

@app.get(
    "/notes/{note_id}",
    response_model=schemas.NoteResponse,
)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
):
    note = crud.get_note_by_id(
        db,
        note_id,
    )

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found",
        )

    return note


# ============================================================
# NOTES - UPDATE
# ============================================================

@app.put(
    "/notes/{note_id}",
    response_model=schemas.NoteResponse,
)
def update_note(
    note_id: int,
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
):
    updated_note = crud.update_note(
        db,
        note_id,
        note,
    )

    if updated_note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found",
        )

    return updated_note


# ============================================================
# NOTES - DELETE
# ============================================================

@app.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    deleted_note = crud.delete_note(
        db,
        note_id,
    )

    if deleted_note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found",
        )

    return {
        "message": "Note deleted successfully",
    }


# ============================================================
# BULK IMPORT
# ============================================================

@app.post("/notes/import")
async def import_notes(
    owner_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected",
        )

    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are allowed",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded",
        )

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        raise HTTPException(
            status_code=400,
            detail="No notes found in file",
        )

    notes = crud.import_notes(
        db,
        owner_id,
        lines,
    )

    if notes is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found",
        )

    return {
        "message": (
            f"{len(notes)} "
            "notes imported successfully"
        ),
    }


# ============================================================
# REPORTS
# ============================================================

@app.get("/reports/tag-summary")
def tag_summary(
    db: Session = Depends(get_db),
):
    return crud.get_tag_summary(db)


@app.get("/reports/long-notes")
def long_notes(
    db: Session = Depends(get_db),
):
    return crud.get_long_notes(db)


@app.get("/reports/user-notes")
def user_notes_report(
    db: Session = Depends(get_db),
):
    return crud.get_user_notes_report(db)








