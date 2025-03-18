from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, database
from src import services
from src import schemas

router = APIRouter()


@router.post("/notes/", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, db: Session = Depends(database.get_db)):
    return crud.create_note(db, title=note.title, content=note.content)


@router.get("/notes/{note_id}", response_model=schemas.Note)
def read_note(note_id: int, db: Session = Depends(database.get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/notes/{note_id}", response_model=schemas.Note)
def update_note(note_id: int, note: schemas.NoteUpdate, db: Session = Depends(database.get_db)):
    note = crud.update_note(db, note_id, content=note.content)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/notes/{note_id}", response_model=dict)
def delete_note(note_id: int, db: Session = Depends(database.get_db)):
    note = crud.delete_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted"}


@router.post("/notes/{note_id}/summarize", response_model=schemas.NoteSummary)
def summarize_note(note_id: int, db: Session = Depends(database.get_db)):
    summary = services.summarize_note(db, note_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"id": note_id, "summary": summary}


@router.get("/analytics/", response_model=schemas.NoteAnalytics)
def analyze_notes(db: Session = Depends(database.get_db)):
    analytics = services.analyze_notes(db)
    if not analytics:
        return {"message": "No notes available for analysis"}
    return analytics
