import os
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime
from src.crud import create_note, get_note, update_note, delete_note, get_all_notes
from src.models import Note, NoteVersion, Base
from unittest.mock import patch, MagicMock
from src.services import analyze_notes, get_gemini_model, summarize_note


class TestNoteFunctions(unittest.TestCase):

    def setUp(self):
        self.db_mock = MagicMock(spec=Session)

    def test_create_note(self):
        title = "Test Note"
        content = "This is a test note."

        self.db_mock.add.return_value = None
        self.db_mock.commit.return_value = None
        self.db_mock.refresh.return_value = None

        note = create_note(self.db_mock, title, content)

        self.db_mock.add.assert_called_once()
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once()
        self.assertEqual(note.title, title)
        self.assertEqual(note.content, content)

    def test_get_note(self):
        note_id = 1
        expected_note = Note(title="Test Note", content="Test Content")
        expected_note.id = note_id
        self.db_mock.get.return_value = expected_note

        note = get_note(self.db_mock, note_id)

        self.db_mock.get.assert_called_once_with(Note, note_id)
        self.assertEqual(note, expected_note)

    def test_get_note_not_found(self):
        note_id = 1
        self.db_mock.get.return_value = None

        note = get_note(self.db_mock, note_id)

        self.db_mock.get.assert_called_once_with(Note, note_id)
        self.assertIsNone(note)

    def test_update_note(self):
        note_id = 1
        initial_content = "Initial Content"
        new_content = "Updated Content"
        note = Note(title="Test Note", content=initial_content)
        note.id = note_id
        self.db_mock.get.return_value = note
        self.db_mock.add.return_value = None
        self.db_mock.commit.return_value = None
        self.db_mock.refresh.return_value = None

        updated_note = update_note(self.db_mock, note_id, new_content)

        self.db_mock.get.assert_called_once_with(Note, note_id)
        self.db_mock.add.assert_called_once()
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once()
        self.assertEqual(updated_note.content, new_content)
        self.assertIsNotNone(updated_note.updated_at)
        self.assertIsInstance(updated_note.updated_at, datetime)
        self.assertIsInstance(self.db_mock.add.call_args[0][0], NoteVersion)
        self.assertEqual(self.db_mock.add.call_args[0][0].content, initial_content)
        self.assertEqual(self.db_mock.add.call_args[0][0].note_id, note_id)

    def test_update_note_not_found(self):
        note_id = 1
        new_content = "Updated Content"
        self.db_mock.get.return_value = None

        updated_note = update_note(self.db_mock, note_id, new_content)

        self.db_mock.get.assert_called_once_with(Note, note_id)
        self.db_mock.add.assert_not_called()
        self.db_mock.commit.assert_not_called()
        self.db_mock.refresh.assert_not_called()
        self.assertIsNone(updated_note)

    def test_delete_note(self):
        note_id = 1
        note = Note(title="Test Note", content="Test Content")
        note.id = note_id
        self.db_mock.get.return_value = note
        self.db_mock.delete.return_value = None
        self.db_mock.commit.return_value = None

        deleted_note = delete_note(self.db_mock, note_id)

        self.db_mock.get.assert_called_once_with(Note, note_id)
        self.db_mock.delete.assert_called_once_with(note)
        self.db_mock.commit.assert_called_once()
        self.assertEqual(deleted_note, note)

    def test_delete_note_not_found(self):
        note_id = 1
        self.db_mock.get.return_value = None
        self.db_mock.delete.return_value = None
        self.db_mock.commit.return_value = None

        deleted_note = delete_note(self.db_mock, note_id)

        self.db_mock.get.assert_called_once_with(Note, note_id)
        self.db_mock.delete.assert_not_called()
        self.db_mock.commit.assert_not_called()
        self.assertIsNone(deleted_note)

    def test_get_all_notes(self):
        note1 = Note(title="Note 1", content="Content 1")
        note2 = Note(title="Note 2", content="Content 2")
        expected_notes = [note1, note2]
        self.db_mock.query.return_value.all.return_value = expected_notes

        notes = get_all_notes(self.db_mock)

        self.db_mock.query.assert_called_once_with(Note)
        self.db_mock.query.return_value.all.assert_called_once()
        self.assertEqual(notes, expected_notes)


class TestNoteAndNoteVersion(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_note(self):
        note = Note(title="Test Note", content="This is a test note.")
        self.session.add(note)
        self.session.commit()

        self.assertIsNotNone(note.id)
        self.assertEqual(note.title, "Test Note")
        self.assertEqual(note.content, "This is a test note.")
        self.assertIsNotNone(note.created_at)
        self.assertIsNotNone(note.updated_at)

    def test_note_default_timestamps(self):
        note = Note(title="Timestamp Test", content="Testing timestamps")
        self.session.add(note)
        self.session.commit()

        self.assertIsNotNone(note.created_at)
        self.assertIsNotNone(note.updated_at)
        self.assertIsInstance(note.created_at, datetime)
        self.assertIsInstance(note.updated_at, datetime)

    def test_note_version_default_timestamps(self):
        note = Note(title="Test Note", content="Initial content")
        self.session.add(note)
        self.session.commit()

        note_version = NoteVersion(note_id=note.id, content="Updated content")
        self.session.add(note_version)
        self.session.commit()

        self.assertIsNotNone(note_version.created_at)
        self.assertIsInstance(note_version.created_at, datetime)

    def test_multiple_note_versions(self):
        note = Note(title="Test Note", content="Initial content")
        self.session.add(note)
        self.session.commit()

        note_version1 = NoteVersion(note_id=note.id, content="Version 1")
        note_version2 = NoteVersion(note_id=note.id, content="Version 2")
        self.session.add_all([note_version1, note_version2])
        self.session.commit()

        self.assertEqual(len(note.versions), 2)
        self.assertEqual(note.versions[0].content, "Version 1")
        self.assertEqual(note.versions[1].content, "Version 2")


class TestGeminiFunctions(unittest.TestCase):
    def setUp(self):
        self.db_mock = MagicMock(spec=Session)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch('src.services.genai')
    def test_get_gemini_model_success(self, mock_genai):
        import src.services
        setattr(src.services, "model", None)

        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        result = get_gemini_model()

        self.assertEqual(result, mock_model)
        mock_genai.configure.assert_called_once_with(api_key="test_api_key")
        mock_genai.GenerativeModel.assert_called_once_with('gemini-1.5-flash')

        self.assertIsNotNone(src.services.model)


    @patch.dict(os.environ, clear=True)
    def test_get_gemini_model_no_api_key(self):
        global model
        model = None
        with self.assertRaises(ValueError) as context:
            get_gemini_model()
        self.assertEqual(str(context.exception), "GEMINI_API_KEY environment variable not set.")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch('src.services.genai')
    @patch('src.crud.get_note')
    def test_summarize_note_success(self, mock_get_note, mock_genai):
        mock_note = {"id": 1, "content": "This is a test note."}
        mock_get_note.return_value = type('Note', (object,), mock_note)
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test summary"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('src.services.get_gemini_model', return_value=mock_model):
            summary = summarize_note(self.db_mock, 1)

        self.assertEqual(summary, "Test summary")
        mock_model.generate_content.assert_called_once_with("Summarize the following note: This is a test note.")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch('src.services.genai')
    @patch('src.crud.get_note')
    def test_summarize_note_note_not_found(self, mock_get_note, mock_genai):
        mock_get_note.return_value = None
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('src.services.get_gemini_model', return_value=mock_model):
            summary = summarize_note(self.db_mock, 1)

        self.assertIsNone(summary)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch('src.services.genai')
    @patch('src.crud.get_note')
    def test_summarize_note_error(self, mock_get_note, mock_genai):
        mock_note = {"id": 1, "content": "This is a test note."}
        mock_get_note.return_value = type('Note', (object,), mock_note)
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("Test error")
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('src.services.get_gemini_model', return_value=mock_model):
            summary = summarize_note(self.db_mock, 1)

        self.assertIsNone(summary)

    @patch('src.crud.get_all_notes')
    def test_analyze_notes_success(self, mock_get_all_notes):
        mock_notes = [
            {"id": 1, "content": "This is the first note."},
            {"id": 2, "content": "This is the second longer note."},
            {"id": 3, "content": "Short note."},
            {"id": 4, "content": "Another very very very long note."},
            {"id": 5, "content": "Another note."},
        ]
        mock_get_all_notes.return_value = [type('Note', (object,), note) for note in mock_notes]

        analytics = analyze_notes(self.db_mock)
        print("Top 3 longest notes:", analytics["top_3_longest_notes"])

        self.assertIsNotNone(analytics)
        self.assertEqual(analytics["total_word_count"], 21)
        self.assertAlmostEqual(analytics["average_note_length"], 4.2)
        self.assertEqual(analytics["most_common_words"][0][0], "note.")
        self.assertEqual(analytics["top_3_longest_notes"][0]["id"], 2)
        self.assertEqual(analytics["top_3_shortest_notes"][0]["id"], 3)

    @patch('src.crud.get_all_notes')
    def test_analyze_notes_no_notes(self, mock_get_all_notes):
        mock_get_all_notes.return_value = []

        analytics = analyze_notes(self.db_mock)

        self.assertIsNone(analytics)

if __name__ == '__main__':
    unittest.main()