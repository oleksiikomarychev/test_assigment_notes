from sqlalchemy.orm import Session
from src.models import Note, NoteVersion
import datetime


def create_note(db: Session, title: str, content: str):
    note = Note(title=title, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_note(db: Session, note_id: int):
    return db.get(Note, note_id)

def update_note(db: Session, note_id: int, content: str):
    note = db.get(Note, note_id)
    if note:
        version = NoteVersion(note_id=note.id, content=note.content)
        db.add(version)
        note.content = content
        note.updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
        db.refresh(note)
    return note


def delete_note(db: Session, note_id: int):
    note = db.get(Note, note_id)
    if note:
        db.delete(note)
        db.commit()
    return note


def get_all_notes(db: Session):
    return db.query(Note).all()
