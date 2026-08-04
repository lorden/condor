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
    event_links = relationship(
        'CalendarEventBookmark',
        back_populates='bookmark',
        cascade='all, delete-orphan',
    )


workstream_categories = Table(
    'workstream_categories',
    Base.metadata,
    Column('workstream_id', Integer, ForeignKey('workstreams.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    workstreams = relationship('Workstream', secondary=workstream_categories, back_populates='categories')


class Workstream(Base):
    __tablename__ = "workstreams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)

    comments = relationship(
        'WorkstreamComment',
        back_populates='workstream',
        cascade='all, delete-orphan',
    )
    links = relationship(
        'WorkstreamLink',
        back_populates='workstream',
        cascade='all, delete-orphan',
    )
    categories = relationship('Category', secondary=workstream_categories, back_populates='workstreams')


class WorkstreamComment(Base):
    __tablename__ = "workstream_comments"

    id = Column(Integer, primary_key=True, index=True)
    workstream_id = Column(Integer, ForeignKey('workstreams.id'), nullable=False, index=True)
    body = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    workstream = relationship('Workstream', back_populates='comments')


class WorkstreamLink(Base):
    __tablename__ = "workstream_links"

    id = Column(Integer, primary_key=True, index=True)
    workstream_id = Column(Integer, ForeignKey('workstreams.id'), nullable=False, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    workstream = relationship('Workstream', back_populates='links')


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class CalendarEventBookmark(Base):
    __tablename__ = "calendar_event_bookmarks"

    event_id = Column(String, primary_key=True, index=True)
    bookmark_id = Column(Integer, ForeignKey('bookmarks.id'), primary_key=True, index=True)
    event_title = Column(String, nullable=True)
    event_start = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    bookmark = relationship('Bookmark', back_populates='event_links')
