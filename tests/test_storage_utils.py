import json
import tempfile
import unittest
from pathlib import Path

from mcp_sequential_thinking.models import ThoughtData, ThoughtStage
from mcp_sequential_thinking.storage_utils import (
    load_thoughts_from_file,
    prepare_thoughts_for_serialization,
    save_thoughts_to_file,
)


class TestStorageUtils(unittest.TestCase):
    """Test cases for low-level storage helper functions."""

    def setUp(self):
        """Set up temporary file paths for storage utility tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.session_file = self.base_path / "session.json"
        self.lock_file = self.base_path / "session.lock"

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_prepare_thoughts_for_serialization_includes_ids(self):
        """Serialized thought data includes IDs for persistence."""
        thought = ThoughtData(
            thought="Persist this thought",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
            stage=ThoughtStage.CONCLUSION,
        )

        serialized = prepare_thoughts_for_serialization([thought])

        self.assertEqual(len(serialized), 1)
        self.assertEqual(serialized[0]["thought"], "Persist this thought")
        self.assertEqual(serialized[0]["id"], str(thought.id))

    def test_save_thoughts_to_file_writes_metadata_and_creates_parents(self):
        """Saving writes thought payloads, metadata, and missing parent directories."""
        nested_session_file = self.base_path / "nested" / "session.json"
        nested_lock_file = self.base_path / "nested" / "session.lock"
        thoughts = [{"thought": "Saved thought"}]
        metadata = {"metadata": {"totalThoughts": 1}}

        save_thoughts_to_file(nested_session_file, thoughts, nested_lock_file, metadata)

        with open(nested_session_file, encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["thoughts"], thoughts)
        self.assertEqual(data["metadata"], {"totalThoughts": 1})
        self.assertIn("lastUpdated", data)

    def test_load_missing_file_returns_empty_list(self):
        """Missing session files load as an empty history."""
        self.assertEqual(load_thoughts_from_file(self.session_file, self.lock_file), [])

    def test_load_non_object_json_returns_empty_list(self):
        """Malformed session shape with a non-object root is ignored."""
        self.session_file.write_text("[]", encoding="utf-8")

        self.assertEqual(load_thoughts_from_file(self.session_file, self.lock_file), [])

    def test_load_non_list_thoughts_returns_empty_list(self):
        """Malformed session shape with non-list thoughts is ignored."""
        self.session_file.write_text('{"thoughts": "not a list"}', encoding="utf-8")

        self.assertEqual(load_thoughts_from_file(self.session_file, self.lock_file), [])

    def test_load_ignores_non_dict_entries(self):
        """Invalid entries in the thoughts list are skipped while valid thoughts load."""
        valid_thought = ThoughtData(
            thought="Valid thought",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
            stage=ThoughtStage.CONCLUSION,
        ).to_dict(include_id=True)
        self.session_file.write_text(
            json.dumps({"thoughts": [valid_thought, "not a thought"]}),
            encoding="utf-8",
        )

        thoughts = load_thoughts_from_file(self.session_file, self.lock_file)

        self.assertEqual(len(thoughts), 1)
        self.assertEqual(thoughts[0].thought, "Valid thought")

    def test_load_corrupted_json_creates_backup_and_returns_empty_list(self):
        """Corrupted JSON is backed up instead of crashing the storage layer."""
        self.session_file.write_text("{not valid json", encoding="utf-8")

        thoughts = load_thoughts_from_file(self.session_file, self.lock_file)

        self.assertEqual(thoughts, [])
        self.assertFalse(self.session_file.exists())
        backup_files = list(self.base_path.glob("session.bak.*"))
        self.assertEqual(len(backup_files), 1)
        self.assertEqual(backup_files[0].read_text(encoding="utf-8"), "{not valid json")


if __name__ == "__main__":
    unittest.main()
