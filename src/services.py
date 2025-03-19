import os
from sqlalchemy.orm import Session
from collections import Counter
import numpy as np
from src import crud
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
model = None

def get_gemini_model():
    global model
    if model is None:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def summarize_note(db: Session, note_id: int):
    note = crud.get_note(db, note_id)
    if not note:
        return None

    model = get_gemini_model()

    prompt = f"Summarize the following note: {note.content}"
    try:
        response = model.generate_content(prompt)
        summary = response.text.strip()
        return summary
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None


def analyze_notes(db: Session):
    notes = crud.get_all_notes(db)
    if not notes:
        return None

    contents = [note.content for note in notes]
    word_counts = [len(content.split()) for content in contents]
    total_word_count = sum(word_counts)
    avg_note_length = np.mean(word_counts)
    all_words = " ".join(contents).split()
    most_common_words = Counter(all_words).most_common(5)
    sorted_notes = sorted(notes, key=lambda note: len(note.content.split()))
    top_3_longest = [{"id": note.id, "length": len(note.content.split())} for note in sorted_notes[3:]]
    top_3_shortest = [{"id": note.id, "length": len(note.content.split())} for note in sorted_notes[:3]]

    return {
        "total_word_count": total_word_count,
        "average_note_length": avg_note_length,
        "most_common_words": most_common_words,
        "top_3_longest_notes": top_3_longest,
        "top_3_shortest_notes": top_3_shortest
    }