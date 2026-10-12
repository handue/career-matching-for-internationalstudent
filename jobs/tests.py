"""Check queueing, ownership, and worker completion without network calls. / 네트워크 없이 작업 등록·소유권·완료 처리를 확인합니다."""

from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from .management.commands.run_collection_worker import Command
from .models import CollectionJob, JobAnalysis


class CollectionTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="student", password="test-password")
        self.client.force_login(self.user)

    def test_queue_returns_before_running_collection(self) -> None:
        with patch("subprocess.run") as run:
            response = self.client.post(reverse("jobs:create_collection"), {
                "search_limit": 5, "analyze_limit": 1, "model": "qwen3:8b",
            })
        self.assertEqual(response.status_code, 202)
        self.assertEqual(CollectionJob.objects.get().status, "queued")
        run.assert_not_called()

    def test_invalid_options_do_not_enqueue(self) -> None:
        response = self.client.post(reverse("jobs:create_collection"), {
            "search_limit": 0, "analyze_limit": 1, "model": "qwen3:8b",
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CollectionJob.objects.exists())

    def test_status_belongs_to_requesting_user(self) -> None:
        owner = get_user_model().objects.create_user(username="another-user")
        job = CollectionJob.objects.create(owner=owner)
        response = self.client.get(reverse("jobs:collection_status", args=[job.pk]))
        self.assertEqual(response.status_code, 404)

    def test_login_and_csrf_are_required(self) -> None:
        anonymous = Client()
        self.assertEqual(anonymous.get(reverse("jobs:dashboard")).status_code, 302)
        protected = Client(enforce_csrf_checks=True)
        protected.force_login(self.user)
        self.assertEqual(protected.post(reverse("jobs:create_collection")).status_code, 403)

    def test_unknown_filter_remains_available(self) -> None:
        for status in ("no", "unknown"):
            JobAnalysis.objects.create(
                source_url=f"https://example.com/{status}", title=status,
                company="Example", location="United States",
                record={"analysis": {"opt_status": status, "opt_evidence": ""}},
            )
        response = self.client.get(reverse("jobs:dashboard"), {"category": "opt", "status": "unknown"})
        self.assertEqual(response.context["total"], 1)
        self.assertEqual(response.context["cards"][0]["status"], "unknown")

    def test_worker_persists_completion_or_failure(self) -> None:
        module = "jobs.management.commands.run_collection_worker"
        temp_root = settings.BASE_DIR / "data" / "results"
        temp_root.mkdir(parents=True, exist_ok=True)
        for code, expected in ((0, "completed"), (1, "failed")):
            job = CollectionJob.objects.create(owner=self.user)
            with tempfile.TemporaryDirectory(dir=temp_root) as directory:
                with patch(f"{module}.subprocess.run", return_value=SimpleNamespace(returncode=code)) as run, \
                     patch(f"{module}.import_analyses", return_value=(1, 0)):
                    Command().process(job, Path(directory).resolve())
                    self.assertEqual(run.call_args.args[0][2:4], ["-m", "job_pipeline.cli"])
            job.refresh_from_db()
            self.assertEqual(job.status, expected)
            self.assertIsNotNone(job.finished_at)
