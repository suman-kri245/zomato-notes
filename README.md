# Zomato Notes API

## Project Overview

Zomato Notes API is a FastAPI-based backend application that allows users to manage notes efficiently. It supports CRUD operations, file import, reports, search algorithms, and AI-assisted note tagging.

---

## Features

- User Management
- Notes CRUD
- File Import (.txt)
- Reports
- Search by Tag
- Quick Search (Binary Search)
- Smart Search
- AI-based Note Tagging
- Background Tasks
- Token Protected Delete API

---

## Tech Stack

- FastAPI
- Python
- SQLAlchemy
- SQLite
- Pydantic
- HTML
- CSS
- JavaScript

---

## Folder Structure

backend/
frontend/
README.md
requirements.txt

---

## Installation

```bash
pip install -r requirements.txt
```

Run Backend

```bash
uvicorn main:app --reload
```

Run Frontend

Open index.html using Live Server.

---

## API Endpoints

- POST /users
- POST /notes
- GET /notes
- GET /notes/{id}
- PUT /notes/{id}
- DELETE /notes/{id}
- POST /notes/import
- GET /reports/tag-summary
- GET /reports/long-notes
- GET /reports/user-notes
- GET /search/tag
- GET /search/tag-quick
- GET /smart-search

---

## Author

Suman Kumari
