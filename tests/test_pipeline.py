"""Check pipeline wiring without network or Ollama. / 네트워크·Ollama 없이 처리 흐름 연결을 검사합니다."""

from pathlib import Path
import unittest
import json
import tempfile
from unittest.mock import patch

from job_pipeline.pipeline import PipelineOptions, run_pipeline, validate_options


class PipelineTests(unittest.TestCase):
    def test_invalid_options_fail_before_loading_integrations(self) -> None:
        with self.assertRaises(ValueError):
            run_pipeline(PipelineOptions(source="ddgs", query=None))
        with self.assertRaises(ValueError):
            validate_options(PipelineOptions(search_limit=0))

    def test_board_configuration_normalizes_provider_and_rejects_invalid_slug(self) -> None:
        from job_pipeline.collection import read_boards
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "boards.json"
            path.write_text(json.dumps([{"provider": "Greenhouse", "board": "nearform"}]))
            self.assertEqual(read_boards(path), [{"provider": "greenhouse", "board": "nearform"}])
            path.write_text(json.dumps([{"provider": "greenhouse", "board": "../invalid"}]))
            with self.assertRaises(ValueError):
                read_boards(path)

    def test_ats_collection_passes_its_report_to_analysis(self) -> None:
        report = Path("ats-report.json")
        options = PipelineOptions(search_limit=3, analyze_limit=2, model="test-model")
        with patch("job_pipeline.collection.collect_jobs", return_value=(report, 3, 0)) as collect, \
             patch("job_pipeline.analysis.reports.analyze_report", return_value=(2, 0)) as analyze, \
             patch("job_pipeline.storage.list_analyses", return_value=0):
            self.assertEqual(run_pipeline(options), 0)
        collect.assert_called_once_with(options.config, 3)
        analyze.assert_called_once_with(report, "test-model", 2, 24)

    def test_empty_failed_collection_does_not_report_success(self) -> None:
        with patch("job_pipeline.collection.collect_jobs", return_value=(Path("report.json"), 0, 1)), \
             patch("job_pipeline.analysis.reports.analyze_report") as analyze:
            self.assertEqual(run_pipeline(PipelineOptions()), 1)
        analyze.assert_not_called()

    def test_report_analysis_calls_extractor_directly(self) -> None:
        from job_pipeline.analysis.reports import analyze_file
        with patch.object(Path, "read_text", return_value="Posting text"), \
             patch("job_pipeline.analysis.reports.analyze_posting", return_value={}) as extract:
            self.assertEqual(analyze_file(Path("posting.txt"), "test-model"), {})
        extract.assert_called_once_with("Posting text", "test-model")


if __name__ == "__main__":
    unittest.main()
