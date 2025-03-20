import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base
from src.crud import create_note, get_note, update_note, delete_note, get_all_notes
from src.services import analyze_notes

db_url = "sqlite:///:memory:"
engine = create_engine(db_url, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_note(db_session):
    note = create_note(db_session, "Test Title", "Test Content")
    assert note.id is not None
    assert note.title == "Test Title"
    assert note.content == "Test Content"

def test_get_note(db_session):
    note = create_note(db_session, "Test", "Content")
    fetched_note = get_note(db_session, note.id)
    assert fetched_note is not None
    assert fetched_note.title == "Test"

def test_update_note(db_session):
    note = create_note(db_session, "Initial Title", "Initial Content")
    updated_note = update_note(db_session, note.id, "Updated Content")
    assert updated_note.content == "Updated Content"

def test_delete_note(db_session):
    note = create_note(db_session, "Title", "Content")
    deleted_note = delete_note(db_session, note.id)
    assert deleted_note is not None
    assert get_note(db_session, note.id) is None

def test_get_all_notes(db_session):
    create_note(db_session, "Note 1", "Content 1")
    create_note(db_session, "Note 2", "Content 2")
    notes = get_all_notes(db_session)
    assert len(notes) == 2

def test_analyze_notes(db_session):
    create_note(db_session, "Note 1", "This is a sample note.")
    create_note(db_session, "Note 2", "Another example note content.")
    stats = analyze_notes(db_session)
    assert stats["total_word_count"] > 0
    assert len(stats["most_common_words"]) > 0
