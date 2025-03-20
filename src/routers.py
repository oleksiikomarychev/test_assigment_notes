from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, database
from src import services
from src import schemas

crud_router = APIRouter()
ai_router = APIRouter()


@crud_router.post("/notes/", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, db: Session = Depends(database.get_db)):
    return crud.create_note(db, title=note.title, content=note.content)


@crud_router.get("/notes/{note_id}", response_model=schemas.Note)
def read_note(note_id: int, db: Session = Depends(database.get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@crud_router.put("/notes/{note_id}", response_model=schemas.Note)
def update_note(note_id: int, note: schemas.NoteUpdate, db: Session = Depends(database.get_db)):
    updated_note = crud.update_note(db, note_id, content=note.content)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note


@crud_router.delete("/notes/{note_id}", response_model=dict)
def delete_note(note_id: int, db: Session = Depends(database.get_db)):
    note = crud.delete_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted"}


@ai_router.post("/notes/{note_id}/summarize", response_model=schemas.NoteSummary)
def summarize_note(note_id: int, db: Session = Depends(database.get_db)):
    summary = services.summarize_note(db, note_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"id": note_id, "summary": summary}


@ai_router.get("/analytics/", response_model=schemas.NoteAnalytics)
def analyze_notes(db: Session = Depends(database.get_db)):
    analytics = services.analyze_notes(db)
    if not analytics:
        raise HTTPException(status_code=404, detail="No notes available for analysis")
    return analytics
