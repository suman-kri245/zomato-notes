# Zomato Notes — AI-Augmented Internal Knowledge Base

Zomato Notes is a full-stack internal knowledge-base application built for capturing, searching, ranking, and retrieving engineering notes efficiently.

## Features

### Part 1 — Core Application

* Create notes
* List notes
* Get a single note
* Update notes
* Delete notes
* User creation
* Tag-based note filtering
* Bulk `.txt` note import
* Token-protected note deletion

### Part 2 — Ranking Engine

* Keyword relevance search
* Insertion-sort based ranking
* Date-based ranking
* Exact title lookup using iterative binary search
* Exact title lookup using recursive binary search
* Quick tag search using linear search

### Part 3 — AI Smart Search

* Semantic search using Sentence Transformers
* `all-MiniLM-L6-v2` embeddings
* Cosine similarity based ranking
* Top 5 semantic search results
* AI-powered automatic note tagging using Gemini
* Optional manual tag during note creation

### Part 4 — Reporting

* Tag summary report
* Long notes report
* User notes report

### Part 5 — Frontend Integration

* Browser-based dashboard
* Create and load notes
* Title search
* Tag search
* Quick tag search
* Semantic Smart Search
* Search results displayed in the browser

## Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* SQLite
* Sentence Transformers
* Scikit-learn
* Google Gemini

### Frontend

* HTML
* CSS
* JavaScript

## Project Structure

```text
zomato-notes/
│
├── backend/
│   ├── main.py
│   ├── crud.py
│   ├── models.py
│   ├── schemas.py
│   ├── algorithms.py
│   ├── semantic_search.py
│   ├── seed.py
│   ├── ranking_dataset.py
│   ├── requirements.txt
│   └── zomato_notes.db
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── mock-data.js
│
├── sample_import.txt
├── .env
├── .gitignore
└── README.md
```

## How to Run

### 1. Open the project

```powershell
cd C:\Users\SUNNY\Desktop\zomato-notes
```

### 2. Activate the virtual environment

```powershell
.\backend\venv\Scripts\activate
```

### 3. Start the FastAPI backend

```powershell
python -m uvicorn backend.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### 4. Start the frontend

Open `frontend/index.html` using VS Code Live Server.

The frontend normally runs at:

```text
http://127.0.0.1:5500
```

## Environment Variables

Create a `.env` file and configure the required API key:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit real API keys or passwords to GitHub.

## Verification

The project was tested through:

* FastAPI Swagger UI
* Browser frontend
* Core note operations
* Ranking search
* Binary search
* Linear search
* Semantic Smart Search
* AI auto-tagging
* Reporting endpoints
* Frontend-to-backend integration

## Author

**Suman Kumari**

