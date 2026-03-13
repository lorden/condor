from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
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

    class Config:
        orm_mode = True

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
    tags: List[TagOut] = []
    click_count: int = 0
    last_accessed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


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
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.hostname:
            return f"https://www.google.com/s2/favicons?domain={parsed.hostname}&sz=32"
    except:
        pass
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
