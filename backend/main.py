import json
import os
import time as time_module
import traceback
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

# Lightweight auto-migrations: add missing columns without losing data
def run_migrations():
    from sqlalchemy import text, inspect
    inspector = inspect(engine)

    # Define migrations as (table, column, sql)
    migrations = [
        ("bookmarks", "favicon_url", "ALTER TABLE bookmarks ADD COLUMN favicon_url TEXT"),
        # Add future migrations here:
        # ("bookmarks", "new_column", "ALTER TABLE bookmarks ADD COLUMN new_column TEXT"),
    ]

    with engine.connect() as conn:
        for table, column, sql in migrations:
            columns = [c["name"] for c in inspector.get_columns(table)]
            if column not in columns:
                print(f"Migration: Adding {column} to {table}")
                conn.execute(text(sql))
                conn.commit()

run_migrations()

app = FastAPI()


class TagOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

# Allow CORS for local extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BookmarkCreate(BaseModel):
    url: str
    title: Optional[str] = None
    tags: Optional[str] = None  # Space-separated tags


class BookmarkOut(BaseModel):
    id: int
    url: str
    title: Optional[str]
    favicon_url: Optional[str] = None
    tags: List[TagOut] = Field(default_factory=list)
    click_count: Optional[int] = 0
    last_accessed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CalendarEventBookmarkCreate(BaseModel):
    bookmark_id: int
    event_title: Optional[str] = None
    event_start: Optional[str] = None


class CalendarEventOut(BaseModel):
    id: str
    mapping_key: str
    recurring_event_id: Optional[str] = None
    summary: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    bookmarks: List[BookmarkOut] = Field(default_factory=list)


@app.get("/bookmarks", response_model=List[BookmarkOut])
def list_bookmarks(q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Bookmark)
    if q:
        search_term = f"%{q.lower()}%"
        query = query.outerjoin(models.Bookmark.tags).filter(
            (models.Bookmark.url.ilike(search_term)) |
            (models.Bookmark.title.ilike(search_term)) |
            (models.Tag.name.ilike(search_term))
        ).distinct()
    # Sort by last_accessed_at descending, nulls last
    query = query.order_by(models.Bookmark.last_accessed_at.desc().nullslast())
    return query.all()


@app.post("/bookmarks/migrate-favicons")
def migrate_favicons(db: Session = Depends(get_db)):
    """Backfill favicon URLs for existing bookmarks that don't have one."""
    bookmarks = db.query(models.Bookmark).filter(models.Bookmark.favicon_url.is_(None)).all()
    updated = 0
    for bookmark in bookmarks:
        favicon_url = get_favicon_url(bookmark.url)
        if favicon_url:
            bookmark.favicon_url = favicon_url
            updated += 1
    db.commit()
    return {"updated": updated}


def get_or_create_tags(db: Session, tag_names: List[str]) -> List[models.Tag]:
    tags = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        tag = db.query(models.Tag).filter(models.Tag.name == name).first()
        if not tag:
            tag = models.Tag(name=name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tags.append(tag)
    return tags


def get_favicon_url(url: str) -> Optional[str]:
    """Generate cached favicon URL from Google's favicon service."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.hostname:
        return f"https://www.google.com/s2/favicons?domain={parsed.hostname}&sz=32"
    return None


@app.post("/bookmarks", response_model=BookmarkOut)
def add_bookmark(bookmark: BookmarkCreate, db: Session = Depends(get_db)):
    favicon_url = get_favicon_url(bookmark.url)
    db_bookmark = models.Bookmark(url=bookmark.url, title=bookmark.title, favicon_url=favicon_url)
    if bookmark.tags:
        tag_names = bookmark.tags.split()
        db_bookmark.tags = get_or_create_tags(db, tag_names)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark


@app.post("/bookmarks/{bookmark_id}/click", response_model=BookmarkOut)
def record_click(bookmark_id: int, db: Session = Depends(get_db)):
    bookmark = db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    bookmark.click_count = (bookmark.click_count or 0) + 1
    bookmark.last_accessed_at = datetime.utcnow()
    db.commit()
    db.refresh(bookmark)
    return bookmark


def _get_setting(key: str) -> Optional[str]:
    """Read a setting value from its own short-lived session."""
    with SessionLocal() as db:
        row = db.query(models.Setting).filter(models.Setting.key == key).first()
        return row.value if row and row.value else None


def parse_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    return parts[1].strip()


def normalize_event_time(event_time: Optional[dict]) -> Optional[str]:
    if not event_time:
        return None
    return event_time.get("dateTime") or event_time.get("date")


async def fetch_primary_calendar_events_today(access_token: str) -> List[dict]:
    local_tz = datetime.now().astimezone().tzinfo
    start_local = datetime.combine(datetime.now(local_tz).date(), time.min, tzinfo=local_tz)
    end_local = start_local + timedelta(days=1)
    params = {
        "timeMin": start_local.astimezone().isoformat(),
        "timeMax": end_local.astimezone().isoformat(),
        "singleEvents": "true",
        "orderBy": "startTime",
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            params=params,
            headers=headers,
        )

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Google token is invalid or expired")
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Google Calendar API error: {response.text}")

    items = response.json().get("items", [])
    return [
        item
        for item in items
        if item.get("status") != "cancelled" and item.get("eventType") != "workingLocation"
    ]


@app.get("/calendar/events/today", response_model=List[CalendarEventOut])
async def get_today_events(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    access_token = parse_bearer_token(authorization)
    events = await fetch_primary_calendar_events_today(access_token)
    mapping_keys = []
    for event in events:
        event_id = event.get("id")
        if not event_id:
            continue
        mapping_keys.append(event.get("recurringEventId") or event_id)

    mappings_by_event_id = {}
    if mapping_keys:
        mappings = (
            db.query(models.CalendarEventBookmark)
            .join(models.CalendarEventBookmark.bookmark)
            .filter(models.CalendarEventBookmark.event_id.in_(mapping_keys))
            .all()
        )
        for mapping in mappings:
            mappings_by_event_id.setdefault(mapping.event_id, []).append(mapping.bookmark)

    result = []
    for event in events:
        event_id = event.get("id")
        if not event_id:
            continue
        recurring_event_id = event.get("recurringEventId")
        mapping_key = recurring_event_id or event_id
        result.append(
            CalendarEventOut(
                id=event_id,
                mapping_key=mapping_key,
                recurring_event_id=recurring_event_id,
                summary=event.get("summary") or "(No title)",
                start_time=normalize_event_time(event.get("start")),
                end_time=normalize_event_time(event.get("end")),
                bookmarks=mappings_by_event_id.get(mapping_key, []),
            )
        )
    return result


@app.post("/calendar/events/{event_id}/bookmarks", response_model=CalendarEventOut)
def link_bookmark_to_event(
    event_id: str,
    payload: CalendarEventBookmarkCreate,
    db: Session = Depends(get_db),
):
    bookmark = db.query(models.Bookmark).filter(models.Bookmark.id == payload.bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    existing = (
        db.query(models.CalendarEventBookmark)
        .filter(
            models.CalendarEventBookmark.event_id == event_id,
            models.CalendarEventBookmark.bookmark_id == payload.bookmark_id,
        )
        .first()
    )
    if not existing:
        db.add(
            models.CalendarEventBookmark(
                event_id=event_id,
                bookmark_id=payload.bookmark_id,
                event_title=payload.event_title,
                event_start=payload.event_start,
            )
        )
        db.commit()

    bookmarks = [
        row.bookmark
        for row in (
            db.query(models.CalendarEventBookmark)
            .join(models.CalendarEventBookmark.bookmark)
            .filter(models.CalendarEventBookmark.event_id == event_id)
            .all()
        )
    ]
    return CalendarEventOut(
        id=event_id,
        mapping_key=event_id,
        summary=payload.event_title or "(No title)",
        start_time=payload.event_start,
        bookmarks=bookmarks,
    )


@app.delete("/calendar/events/{event_id}/bookmarks/{bookmark_id}")
def unlink_bookmark_from_event(event_id: str, bookmark_id: int, db: Session = Depends(get_db)):
    mapping = (
        db.query(models.CalendarEventBookmark)
        .filter(
            models.CalendarEventBookmark.event_id == event_id,
            models.CalendarEventBookmark.bookmark_id == bookmark_id,
        )
        .first()
    )
    if not mapping:
        raise HTTPException(status_code=404, detail="Event-bookmark link not found")
    db.delete(mapping)
    db.commit()
    return {"status": "ok"}


# Jira: combined stream of comments and status updates for a project.
# In-memory cache keyed by project key, 10-minute TTL.

JIRA_CACHE_TTL_SECONDS = 600
JIRA_MAX_ISSUES = 50
JIRA_MAX_UPDATES = 100
JIRA_EPIC_LINK_FIELD = "customfield_10014"

_jira_cache: Dict[str, Tuple[float, List[dict]]] = {}
_jira_releases_cache: Dict[str, Tuple[float, List[dict]]] = {}


class JiraUpdate(BaseModel):
    id: str
    type: str  # "comment" or "status"
    issue_key: str
    issue_url: str
    issue_summary: str
    epic_key: Optional[str] = None
    epic_summary: Optional[str] = None
    epic_url: Optional[str] = None
    author: str
    timestamp: Optional[str] = None
    body: Optional[str] = None
    from_status: Optional[str] = None
    to_status: Optional[str] = None


class JiraUpdatesOut(BaseModel):
    project: str
    cached: bool
    fetched_at: float
    updates: List[JiraUpdate]


def _adf_to_text(body: Any) -> str:
    """Best-effort plain-text extraction from an Atlassian Document Format node."""
    if isinstance(body, str):
        return body
    if not isinstance(body, (dict, list)):
        return ""
    parts: List[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "text":
                parts.append(node.get("text") or "")
            elif node.get("type") == "hardBreak":
                parts.append("\n")
            for child in node.get("content") or []:
                walk(child)
            if node.get("type") in {"paragraph", "heading", "bulletList", "orderedList", "listItem"}:
                parts.append("\n")
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(body)
    return "\n".join(line.strip() for line in "".join(parts).splitlines() if line.strip()).strip()


def _epic_from_issue(fields: dict) -> Tuple[Optional[str], Optional[str]]:
    parent = fields.get("parent")
    if parent and (parent.get("fields", {}).get("issuetype", {}) or {}).get("name") == "Epic":
        return parent.get("key"), (parent.get("fields", {}) or {}).get("summary")
    epic_link = fields.get(JIRA_EPIC_LINK_FIELD)
    if isinstance(epic_link, str) and epic_link:
        return epic_link, None
    return None, None


async def _fetch_jira_updates(project: str) -> List[dict]:
    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = _get_setting("jira_token") or os.environ.get("JIRA_API_TOKEN", "")
    if not (base_url and email and token):
        raise HTTPException(
            status_code=500,
            detail="Jira credentials not configured (set JIRA_BASE_URL, JIRA_EMAIL, and a Jira token via /settings or JIRA_API_TOKEN).",
        )

    safe_project = project.replace('"', '\\"')
    jql = f'project = "{safe_project}" ORDER BY updated DESC'
    issue_fields = [
        "summary",
        "status",
        "parent",
        "issuetype",
        "comment",
        "updated",
        JIRA_EPIC_LINK_FIELD,
    ]

    auth = (email, token)
    search_url = f"{base_url}/rest/api/3/search/jql"
    async with httpx.AsyncClient(timeout=30.0, auth=auth) as client:
        response = await client.post(
            search_url,
            json={
                "jql": jql,
                "fields": issue_fields,
                "expand": "changelog",
                "maxResults": JIRA_MAX_ISSUES,
            },
        )
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Jira credentials are invalid.")
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Jira API error: {response.text}")
        data = response.json()

        issues = data.get("issues", [])

        epic_keys_to_lookup = set()
        for issue in issues:
            epic_key, epic_summary = _epic_from_issue(issue.get("fields") or {})
            if epic_key and not epic_summary:
                epic_keys_to_lookup.add(epic_key)

        epic_summary_by_key: Dict[str, str] = {}
        if epic_keys_to_lookup:
            keys_csv = ",".join(f'"{k}"' for k in epic_keys_to_lookup)
            epic_response = await client.post(
                search_url,
                json={
                    "jql": f"key in ({keys_csv})",
                    "fields": ["summary"],
                    "maxResults": len(epic_keys_to_lookup),
                },
            )
            if epic_response.status_code < 400:
                for ei in epic_response.json().get("issues", []):
                    summary = (ei.get("fields") or {}).get("summary")
                    if ei.get("key") and summary:
                        epic_summary_by_key[ei["key"]] = summary

    updates: List[dict] = []
    for issue in issues:
        issue_key = issue.get("key")
        if not issue_key:
            continue
        fields = issue.get("fields") or {}
        issue_url = f"{base_url}/browse/{issue_key}"
        issue_summary = fields.get("summary") or ""

        epic_key, epic_summary = _epic_from_issue(fields)
        if epic_key and not epic_summary:
            epic_summary = epic_summary_by_key.get(epic_key)
        epic_url = f"{base_url}/browse/{epic_key}" if epic_key else None

        for comment in (fields.get("comment") or {}).get("comments", []) or []:
            author = (comment.get("author") or {}).get("displayName") or "Unknown"
            updates.append({
                "id": f"comment-{issue_key}-{comment.get('id')}",
                "type": "comment",
                "issue_key": issue_key,
                "issue_url": issue_url,
                "issue_summary": issue_summary,
                "epic_key": epic_key,
                "epic_summary": epic_summary,
                "epic_url": epic_url,
                "author": author,
                "timestamp": comment.get("updated") or comment.get("created"),
                "body": _adf_to_text(comment.get("body")),
                "from_status": None,
                "to_status": None,
            })

        for history in (issue.get("changelog") or {}).get("histories", []) or []:
            author = (history.get("author") or {}).get("displayName") or "Unknown"
            created = history.get("created")
            for item in history.get("items") or []:
                if item.get("field") != "status":
                    continue
                updates.append({
                    "id": f"status-{issue_key}-{history.get('id')}-{item.get('from') or ''}-{item.get('to') or ''}",
                    "type": "status",
                    "issue_key": issue_key,
                    "issue_url": issue_url,
                    "issue_summary": issue_summary,
                    "epic_key": epic_key,
                    "epic_summary": epic_summary,
                    "epic_url": epic_url,
                    "author": author,
                    "timestamp": created,
                    "body": None,
                    "from_status": item.get("fromString"),
                    "to_status": item.get("toString"),
                })

    updates.sort(key=lambda u: u.get("timestamp") or "", reverse=True)
    return updates[:JIRA_MAX_UPDATES]


@app.get("/jira/updates", response_model=JiraUpdatesOut)
async def get_jira_updates(project: Optional[str] = None, refresh: bool = False):
    project = (project or os.environ.get("JIRA_PROJECT") or "").strip()
    if not project:
        raise HTTPException(
            status_code=400,
            detail="No Jira project configured. Set JIRA_PROJECT in the backend env or pass `?project=KEY`.",
        )

    now = time_module.time()
    cached = _jira_cache.get(project)
    if not refresh and cached and now - cached[0] < JIRA_CACHE_TTL_SECONDS:
        return JiraUpdatesOut(project=project, cached=True, fetched_at=cached[0], updates=cached[1])

    try:
        updates = await _fetch_jira_updates(project)
    except HTTPException:
        raise
    except Exception as exc:  # personal app: surface full traceback to the client
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Jira fetch failed: {exc!r}\n\n{tb}",
        ) from exc
    _jira_cache[project] = (now, updates)
    return JiraUpdatesOut(project=project, cached=False, fetched_at=now, updates=updates)


class JiraRelease(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    released: bool = False
    archived: bool = False
    overdue: Optional[bool] = None
    release_date: Optional[str] = None
    start_date: Optional[str] = None
    user_release_date: Optional[str] = None
    url: Optional[str] = None


class JiraReleasesOut(BaseModel):
    project: str
    cached: bool
    fetched_at: float
    releases: List[JiraRelease]


async def _fetch_jira_releases(project: str) -> List[dict]:
    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = _get_setting("jira_token") or os.environ.get("JIRA_API_TOKEN", "")
    if not (base_url and email and token):
        raise HTTPException(
            status_code=500,
            detail="Jira credentials not configured (set JIRA_BASE_URL, JIRA_EMAIL, and a Jira token via /settings or JIRA_API_TOKEN).",
        )

    auth = (email, token)
    async with httpx.AsyncClient(timeout=30.0, auth=auth) as client:
        response = await client.get(f"{base_url}/rest/api/3/project/{project}/versions")
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Jira credentials are invalid.")
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Jira API error: {response.text}")
        versions = response.json()

    results: List[dict] = []
    for version in versions:
        vid = str(version.get("id") or "")
        name = version.get("name") or ""
        results.append({
            "id": vid,
            "name": name,
            "description": version.get("description"),
            "released": bool(version.get("released")),
            "archived": bool(version.get("archived")),
            "overdue": version.get("overdue"),
            "release_date": version.get("releaseDate") or version.get("userReleaseDate"),
            "start_date": version.get("startDate") or version.get("userStartDate"),
            "user_release_date": version.get("userReleaseDate"),
            "url": f"{base_url}/projects/{project}/versions/{vid}" if vid else None,
        })

    # Most recent first; releases without a date sink to the bottom.
    results.sort(
        key=lambda r: (r.get("release_date") or "0000-00-00"),
        reverse=True,
    )
    return results


@app.get("/jira/releases", response_model=JiraReleasesOut)
async def get_jira_releases(project: Optional[str] = None, refresh: bool = False):
    project = (project or os.environ.get("JIRA_PROJECT") or "").strip()
    if not project:
        raise HTTPException(
            status_code=400,
            detail="No Jira project configured. Set JIRA_PROJECT in the backend env or pass `?project=KEY`.",
        )

    now = time_module.time()
    cached = _jira_releases_cache.get(project)
    if not refresh and cached and now - cached[0] < JIRA_CACHE_TTL_SECONDS:
        return JiraReleasesOut(project=project, cached=True, fetched_at=cached[0], releases=cached[1])

    try:
        releases = await _fetch_jira_releases(project)
    except HTTPException:
        raise
    except Exception as exc:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Jira releases fetch failed: {exc!r}\n\n{tb}",
        ) from exc
    _jira_releases_cache[project] = (now, releases)
    return JiraReleasesOut(project=project, cached=False, fetched_at=now, releases=releases)


# GitHub: open pull requests that need my review or that I authored.
# Uses the search API with `@me` so the token's user is resolved server-side.

GITHUB_CACHE_TTL_SECONDS = 600
GITHUB_API = "https://api.github.com"

_github_cache: Dict[str, Tuple[float, Dict[str, List[dict]]]] = {}


class GitHubPullRequest(BaseModel):
    id: str
    number: int
    title: str
    url: str
    repo: str
    author: Optional[str] = None
    author_url: Optional[str] = None
    author_avatar_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    draft: bool = False
    category: str  # "review_requested" or "authored"


class GitHubPullRequestsOut(BaseModel):
    cached: bool
    fetched_at: float
    review_requested: List[GitHubPullRequest]
    authored: List[GitHubPullRequest]


def _repo_from_pr_url(url: str) -> str:
    # https://api.github.com/repos/{owner}/{name}/issues/{n} → "owner/name"
    try:
        parts = url.split("/repos/", 1)[1].split("/")
        return f"{parts[0]}/{parts[1]}"
    except (IndexError, AttributeError):
        return ""


def _normalize_pr(item: dict, category: str) -> dict:
    user = item.get("user") or {}
    pr = item.get("pull_request") or {}
    return {
        "id": f"{category}-{item.get('id')}",
        "number": item.get("number") or 0,
        "title": item.get("title") or "",
        "url": item.get("html_url") or "",
        "repo": _repo_from_pr_url(item.get("repository_url") or ""),
        "author": user.get("login"),
        "author_url": user.get("html_url"),
        "author_avatar_url": user.get("avatar_url"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "draft": bool(pr.get("draft") or item.get("draft")),
        "category": category,
    }


async def _github_search(client: httpx.AsyncClient, query: str) -> List[dict]:
    response = await client.get(
        f"{GITHUB_API}/search/issues",
        params={"q": query, "per_page": 50, "sort": "updated", "order": "desc"},
    )
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="GitHub token is invalid or expired.")
    if response.status_code == 403:
        raise HTTPException(status_code=403, detail=f"GitHub API forbidden: {response.text}")
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"GitHub API error: {response.text}")
    return response.json().get("items", []) or []


async def _fetch_github_pull_requests() -> Dict[str, List[dict]]:
    token = _get_setting("github_token") or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise HTTPException(
            status_code=500,
            detail="GitHub token not configured (set via /settings or GITHUB_TOKEN env).",
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
        review_items = await _github_search(
            client, "is:pr is:open review-requested:@me archived:false"
        )
        authored_items = await _github_search(
            client, "is:pr is:open author:@me archived:false"
        )

    return {
        "review_requested": [_normalize_pr(i, "review_requested") for i in review_items],
        "authored": [_normalize_pr(i, "authored") for i in authored_items],
    }


@app.get("/github/pull-requests", response_model=GitHubPullRequestsOut)
async def get_github_pull_requests(refresh: bool = False):
    cache_key = "default"
    now = time_module.time()
    cached = _github_cache.get(cache_key)
    if not refresh and cached and now - cached[0] < GITHUB_CACHE_TTL_SECONDS:
        data = cached[1]
        return GitHubPullRequestsOut(
            cached=True,
            fetched_at=cached[0],
            review_requested=data["review_requested"],
            authored=data["authored"],
        )

    try:
        data = await _fetch_github_pull_requests()
    except HTTPException:
        raise
    except Exception as exc:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"GitHub fetch failed: {exc!r}\n\n{tb}",
        ) from exc

    _github_cache[cache_key] = (now, data)
    return GitHubPullRequestsOut(
        cached=False,
        fetched_at=now,
        review_requested=data["review_requested"],
        authored=data["authored"],
    )


# Settings: secret-shaped tokens stored locally so they can be configured from the UI.
# GET reports whether each token is set (never the value); PUT writes/clears.

class SettingsOut(BaseModel):
    jira_token_set: bool
    github_token_set: bool
    jira_swimlane_authors: List[str] = Field(default_factory=list)


class SettingsUpdate(BaseModel):
    # None = leave untouched, "" = clear, anything else = set
    jira_token: Optional[str] = None
    github_token: Optional[str] = None
    # Empty list is meaningful (= "no filter"), so use a sentinel for "leave alone".
    jira_swimlane_authors: Optional[List[str]] = None


def _decode_authors(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return []
    return [str(item) for item in parsed if isinstance(item, str) and item.strip()]


def _settings_status(db: Session) -> SettingsOut:
    rows = {row.key: row for row in db.query(models.Setting).all()}
    return SettingsOut(
        jira_token_set=bool(rows.get("jira_token") and rows["jira_token"].value),
        github_token_set=bool(rows.get("github_token") and rows["github_token"].value),
        jira_swimlane_authors=_decode_authors(
            rows["jira_swimlane_authors"].value if "jira_swimlane_authors" in rows else None
        ),
    )


def _apply_setting(db: Session, key: str, value: str) -> None:
    existing = db.query(models.Setting).filter(models.Setting.key == key).first()
    if value:
        if existing:
            existing.value = value
        else:
            db.add(models.Setting(key=key, value=value))
    elif existing:
        db.delete(existing)


@app.get("/settings", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_db)):
    return _settings_status(db)


@app.put("/settings", response_model=SettingsOut)
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db)):
    touched_jira = False
    touched_github = False
    if payload.jira_token is not None:
        _apply_setting(db, "jira_token", payload.jira_token)
        touched_jira = True
    if payload.github_token is not None:
        _apply_setting(db, "github_token", payload.github_token)
        touched_github = True
    if payload.jira_swimlane_authors is not None:
        cleaned = [s.strip() for s in payload.jira_swimlane_authors if s and s.strip()]
        _apply_setting(db, "jira_swimlane_authors", json.dumps(cleaned))
    db.commit()

    if touched_jira:
        _jira_cache.clear()
        _jira_releases_cache.clear()
    if touched_github:
        _github_cache.clear()

    return _settings_status(db)
