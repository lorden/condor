# Condor Chrome Extension

This extension replaces your Chrome new tab page with a Vue.js app for managing bookmarks.

## Features
- New tab override with custom UI
- Bookmark list with search
- Add bookmarks from the new tab page, keyboard shortcut, or context menu
- Vue.js + Tailwind CSS frontend
- FastAPI backend for bookmark storage

## Setup
1. **Frontend**
   - All code is in `src/`.
   - Install dependencies: `npm install` (Vue, Tailwind)
   - Build and load as unpacked extension in Chrome.

2. **Backend**
   - FastAPI app in `backend/`.
   - Python dependencies are managed with `uv` (`backend/pyproject.toml`, `backend/uv.lock`).
   - Requires Python 3.14+.
   - Local backend commands:
     - `cd backend`
     - `uv sync`
     - `uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
   - Docker setup provided.
   - Run with `docker-compose up`.

## Next Steps
- Add edit/delete bookmark actions.
- Improve tag management and filtering.

## Development Stack
- Frontend: Vue.js, Tailwind CSS
- Backend: Python, FastAPI (optional)

---
This project is for local, single-user use. Security and privacy are minimal.
