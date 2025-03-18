from pydantic import BaseModel
from datetime import datetime
from typing import List


class NoteBase(BaseModel):
    title: str
    content: str


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    content: str


class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class NoteSummary(BaseModel):
    id: int
    summary: str


class NoteAnalytics(BaseModel):
    total_word_count: int
    average_note_length: float
    most_common_words: List[tuple[str, int]]
    top_3_longest_notes: List[dict]
    top_3_shortest_notes: List[dict]
