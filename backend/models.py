from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


bookmark_tags = Table(
    'bookmark_tags',
    Base.metadata,
    Column('bookmark_id', Integer, ForeignKey('bookmarks.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    bookmarks = relationship('Bookmark', secondary=bookmark_tags, back_populates='tags')


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True, index=True)
    favicon_url = Column(String, nullable=True)
    click_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime, nullable=True, index=True)

    tags = relationship('Tag', secondary=bookmark_tags, back_populates='bookmarks')
