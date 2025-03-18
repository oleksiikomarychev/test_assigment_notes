from sqlalchemy.orm import Session
from .models import Note, NoteVersion
from datetime import datetime


def create_note(db: Session, title: str, content: str):
    note = Note(title=title, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_note(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()


def update_note(db: Session, note_id: int, content: str):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note:
        version = NoteVersion(note_id=note.id, content=note.content)
        db.add(version)
        note.content = content
        note.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(note)
    return note


def delete_note(db: Session, note_id: int):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note:
        db.delete(note)
        db.commit()
    return note


def get_all_notes(db: Session):
    return db.query(Note).all()
