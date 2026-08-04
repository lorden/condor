# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Condor is a Chrome new-tab-override extension (Manifest V3) that pairs a Vue 3 + Tailwind frontend with a local FastAPI backend for bookmark storage and Google Calendar integration. It is a single-user, local-only app — security and auth are deliberately minimal.

## Commands

Frontend (repo root):
- `npm install` — install Vite/Vue deps.
- `npm run dev` — Vite dev server (rarely useful; the extension runs from `dist/`).
- `npm run build` — Vite build into `dist/`. **Required before reloading the unpacked extension in Chrome**, because `manifest.json` points `chrome_url_overrides.newtab` at `dist/src/newtab.html`.

Backend (`backend/`, Python 3.14+, managed with `uv`):
- `cd backend && uv sync` — install deps from `pyproject.toml` / `uv.lock`.
- `uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload` — local dev server.
- `docker-compose up` (from repo root) — containerized backend; persists SQLite to `./data/condor.db` via the `./data:/app/data` volume mount.

There is no test suite or linter configured.

## Versioning

The extension follows semantic versioning. **`package.json` is the single source of truth**; `scripts/sync-version.js` stamps that version into `manifest.json` and `manifest.example.json` (it runs automatically via the `prebuild` hook and the `npm version` lifecycle — never edit manifest versions by hand).

Bump the version with every user-visible change, in the same commit as the change:
- **patch** — bug fixes, styling tweaks, copy changes.
- **minor** — new features that don't break existing behavior (new page, new endpoint, new menu item or shortcut).
- **major** — breaking changes: destructive DB schema changes, removed features, or manifest permission changes that require user re-consent.

Backend-only changes count too (the backend ships with the repo); use the same rules.

## Architecture

Three coordinating pieces, communicating across two trust boundaries (extension ↔ backend over HTTP, popup ↔ service worker over `chrome.runtime` messages):

1. **Vue new-tab page** (`src/App.vue`, `src/main.js`, `src/newtab.html`) — built into `dist/` and loaded as the new tab. Calls the backend at `http://localhost:8000` (hard-coded in `src/bookmarks.js`; also listed in `manifest.json` `host_permissions`). Styling: hand-rolled Carbon Design System g100 dark theme in `src/styles.css` (no `@carbon/styles` SCSS pipeline — tokens, components, and utilities are written by hand using CSS variables). IBM Plex Sans/Mono are loaded from Google Fonts via `<link>` in `newtab.html`. Class naming follows `cds-*` (tile, btn, tag, input, select, list, notification, combobox).

2. **Background service worker** (`src/background.js`) — three responsibilities:
   - **Add-bookmark entry points**: `Alt+Shift+S` keyboard command and the right-click context menu both open `chrome://newtab?addBookmark=1&url=…&title=…`; the Vue app reads those query params on load to pre-fill the add form.
   - **Meeting suggestion capture**: maintains an in-memory `meetingContexts` array (sent from the Vue app via `update-meeting-contexts` messages whenever today's calendar is fetched). While the current time falls inside an active meeting window, listeners on `chrome.tabs.onActivated`/`onUpdated`/`chrome.windows.onFocusChanged` capture each visited URL into `chrome.storage.local` under `meetingSuggestionsV1`, keyed by `mappingKey` (= recurring series ID when available, else event ID). URLs are normalized (http/https only, hash stripped), deduped per-tab within a 20s window, and capped at 75 per meeting.
   - **Bulk open**: `open-event-bookmarks` message opens an array of links in a new window and closes the originating tab on full success.

3. **FastAPI backend** (`backend/main.py`, `models.py`, `database.py`) — SQLite at `/app/data/condor.db` (override via `DATABASE_PATH` env). Four tables: `bookmarks`, `tags` (many-to-many via `bookmark_tags`), `calendar_event_bookmarks` (event ↔ bookmark mapping), and `settings` (key/value secrets — currently `jira_token` and `github_token`). Calendar endpoints proxy Google Calendar v3 using a Bearer token forwarded from the extension (the extension obtains it via `chrome.identity.getAuthToken`); the backend itself stores no Google credentials. Jira endpoints (`GET /jira/updates`) proxy `/rest/api/3/search` using **server-side config**: `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_PROJECT` come from env; the API token is read from the `settings` table first, falling back to `JIRA_API_TOKEN`. Project key is overridable per request via `?project=KEY`. Results are cached in-memory per-project for 10 minutes (`JIRA_CACHE_TTL_SECONDS`); pass `refresh=1` to bypass. GitHub endpoint (`GET /github/pull-requests`) follows the same pattern: token from `settings` first, fallback to `GITHUB_TOKEN`. Cached 10 minutes (`GITHUB_CACHE_TTL_SECONDS`). `GET /settings` returns booleans only (`jira_token_set`, `github_token_set`) — never the values; `PUT /settings` accepts `{jira_token?, github_token?}` where omitted = leave untouched, empty string = clear, anything else = set. The frontend uses these booleans as feature flags to gate the corresponding views.

### Key cross-cutting conventions

- **Recurring meetings use `recurringEventId` as the mapping key** so that links and learned suggestions persist across instances of the same series. Both `GET /calendar/events/today` and the background suggestion store rely on this — keep them in sync if you change one.
- **Schema migrations**: there is no Alembic. `run_migrations()` in `backend/main.py` applies idempotent `ALTER TABLE` statements on startup against an `inspect`-discovered column list. Add new columns by appending a tuple to the `migrations` list, not by editing the model alone.
- **Build artifacts are committed**: `dist/` is checked in (the extension loads from it). After changing frontend code, rebuild and commit `dist/` together with the source change so the loaded extension stays consistent.
- **OAuth client ID is in `manifest.json`** (`oauth2.client_id`). It must be a Chrome Extension OAuth client with the `calendar.readonly` scope; the same token is forwarded to the backend as `Authorization: Bearer …`.

## Python conventions

Per the user's global preferences: this project uses Python 3.14+, `uv` for env/deps, and `pyproject.toml` (no `requirements.txt` / `setup.py`). Keep it that way.
