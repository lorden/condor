# Condor Chrome Extension

This extension replaces your Chrome new tab page with a Vue.js app for managing bookmarks.

## Features
- New tab override with custom UI
- Bookmark list with search
- Add bookmarks from the new tab page, keyboard shortcut, or context menu
- Today's Google Calendar meetings on the main page
- Associate existing bookmarks with each meeting
- Passive smart suggestions: during active meeting windows, visited tabs are learned and suggested next time
- One-click open suggested URLs (manual control remains primary)
- Vue.js + Tailwind CSS frontend
- FastAPI backend for bookmark storage

## Setup
1. **Frontend**
   - All code is in `src/`.
   - Install dependencies: `npm install` (Vue, Tailwind)
   - Copy `manifest.example.json` to `manifest.json` (gitignored) and set `oauth2.client_id` to your Chrome Extension OAuth client ID.
   - Make sure the OAuth client has scope: `https://www.googleapis.com/auth/calendar.readonly`.
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
- The database includes `calendar_event_bookmarks`, mapping meetings to bookmarks (uses recurring series IDs when available so recurring meetings keep their links).

3. **Smart suggestion behavior**
   - While a meeting is in progress, the extension listens to active tab changes and stores visited URLs locally per recurring meeting series.
   - Next time the same recurring meeting appears, top URLs are shown as suggestions.
   - This is assistive only: manual bookmark linking and opening stays fully available.

## Next Steps
- Add edit/delete bookmark actions.
- Improve tag management and filtering.

## Development Stack
- Frontend: Vue.js, Tailwind CSS
- Backend: Python, FastAPI (optional)

---
This project is for local, single-user use. Security and privacy are minimal.
