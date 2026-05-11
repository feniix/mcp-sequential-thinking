import asyncio
import importlib
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock


class FakeContext:
    def __init__(self) -> None:
        self.progress_calls: list[tuple[float, float]] = []

    async def report_progress(self, progress: float, total: float) -> None:
        self.progress_calls.append((progress, total))


class TestServerTools(unittest.TestCase):
    """Test cases for the MCP server tool functions."""

    def setUp(self):
        """Import the server with storage isolated to a temporary directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env_patch = mock.patch.dict(os.environ, {"MCP_STORAGE_DIR": self.temp_dir.name})
        self.env_patch.start()

        import mcp_sequential_thinking.server as server

        self.server = importlib.reload(server)

    def tearDown(self):
        """Clean up temporary storage and environment changes."""
        self.env_patch.stop()
        self.temp_dir.cleanup()

    def process_thought(
        self,
        *,
        thought: str,
        thought_number: int,
        total_thoughts: int,
        next_thought_needed: bool,
        stage: str,
        tags: list[str] | None = None,
        axioms_used: list[str] | None = None,
        assumptions_challenged: list[str] | None = None,
        ctx: Any = None,
    ) -> dict[str, Any]:
        """Run the async process_thought tool from synchronous tests."""
        return asyncio.run(
            self.server.process_thought(
                thought=thought,
                thought_number=thought_number,
                total_thoughts=total_thoughts,
                next_thought_needed=next_thought_needed,
                stage=stage,
                tags=tags or [],
                axioms_used=axioms_used or [],
                assumptions_challenged=assumptions_challenged or [],
                ctx=ctx,
            )
        )

    def test_process_thought_stores_and_analyzes_thought(self):
        """Processing a valid thought stores it and returns analysis."""
        ctx = FakeContext()

        result = self.process_thought(
            thought="Define the problem clearly",
            thought_number=1,
            total_thoughts=4,
            next_thought_needed=True,
            stage="Problem Definition",
            tags=["scope"],
            axioms_used=["clarity"],
            assumptions_challenged=["the problem is obvious"],
            ctx=ctx,
        )

        analysis = result["thoughtAnalysis"]
        self.assertEqual(analysis["currentThought"]["thoughtNumber"], 1)
        self.assertEqual(analysis["currentThought"]["stage"], "Problem Definition")
        self.assertEqual(analysis["analysis"]["progress"], 25.0)
        self.assertEqual(ctx.progress_calls, [(0, 4)])

        stored_thoughts = self.server.storage.get_all_thoughts()
        self.assertEqual(len(stored_thoughts), 1)
        self.assertEqual(stored_thoughts[0].thought, "Define the problem clearly")

    def test_process_thought_returns_error_for_invalid_stage(self):
        """Invalid input is reported as a failed tool response."""
        result = self.process_thought(
            thought="This should not be stored",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
            stage="Invalid Stage",
        )

        self.assertEqual(result["status"], "failed")
        self.assertIn("Invalid thinking stage", result["error"])
        self.assertEqual(self.server.storage.get_all_thoughts(), [])

    def test_generate_summary_and_clear_history(self):
        """Summary reflects stored thoughts and clear_history persists an empty session."""
        self.process_thought(
            thought="Research the existing behavior",
            thought_number=1,
            total_thoughts=2,
            next_thought_needed=True,
            stage="Research",
            tags=["coverage"],
        )

        summary = self.server.generate_summary()
        self.assertEqual(summary["summary"]["totalThoughts"], 1)
        self.assertEqual(summary["summary"]["stages"], {"Research": 1})

        clear_result = self.server.clear_history()
        self.assertEqual(clear_result, {"status": "success", "message": "Thought history cleared"})
        self.assertEqual(self.server.storage.get_all_thoughts(), [])

    def test_export_and_import_session_round_trip(self):
        """Exporting and importing through server tools preserves thought history."""
        self.process_thought(
            thought="Conclude with evidence",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
            stage="Conclusion",
        )
        export_file = Path(self.temp_dir.name) / "exports" / "session.json"

        export_result = self.server.export_session(str(export_file))
        self.assertEqual(export_result["status"], "success")
        self.assertTrue(export_file.exists())

        self.server.clear_history()
        self.assertEqual(self.server.storage.get_all_thoughts(), [])

        import_result = self.server.import_session(str(export_file))
        self.assertEqual(import_result["status"], "success")
        stored_thoughts = self.server.storage.get_all_thoughts()
        self.assertEqual(len(stored_thoughts), 1)
        self.assertEqual(stored_thoughts[0].thought, "Conclude with evidence")

    def test_tool_errors_are_reported_as_failed_responses(self):
        """Storage failures are returned to MCP clients instead of escaping."""
        with mock.patch.object(
            self.server.storage, "get_all_thoughts", side_effect=RuntimeError("summary failed")
        ):
            summary_result = self.server.generate_summary()

        with mock.patch.object(
            self.server.storage, "clear_history", side_effect=RuntimeError("clear failed")
        ):
            clear_result = self.server.clear_history()

        with mock.patch.object(
            self.server.storage, "export_session", side_effect=RuntimeError("export failed")
        ):
            export_result = self.server.export_session("unused.json")

        with mock.patch.object(
            self.server.storage, "import_session", side_effect=RuntimeError("import failed")
        ):
            import_result = self.server.import_session("unused.json")

        self.assertEqual(summary_result, {"error": "summary failed", "status": "failed"})
        self.assertEqual(clear_result, {"error": "clear failed", "status": "failed"})
        self.assertEqual(export_result, {"error": "export failed", "status": "failed"})
        self.assertEqual(import_result, {"error": "import failed", "status": "failed"})


if __name__ == "__main__":
    unittest.main()
