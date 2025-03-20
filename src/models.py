from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    versions = relationship("NoteVersion", back_populates="note")


class NoteVersion(Base):
    __tablename__ = "note_versions"
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    note = relationship("Note", back_populates="versions")
