"""Process the DB queue outside the web server. / 웹 서버와 별도로 DB 작업 큐를 처리합니다."""

import fcntl
from pathlib import Path
import subprocess
import sys
import time
from argparse import ArgumentParser
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from jobs.models import CollectionJob
from jobs.services import import_analyses


class Command(BaseCommand):
    help = "Run a single local collection worker (macOS/Linux)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--once", action="store_true", help="Process at most one queued job and exit")

    def handle(self, *args: object, **options: object) -> None:
        directory: Path = settings.BASE_DIR / "data" / "results" / "django_worker"
        directory.mkdir(parents=True, exist_ok=True)
        # One worker protects shared CLI report files. / 작업자 하나만 실행해 CLI 보고서 파일 충돌을 막습니다.
        with (directory / "worker.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise CommandError("A collection worker is already running") from error
            CollectionJob.objects.filter(status=CollectionJob.Status.RUNNING).update(
                status=CollectionJob.Status.FAILED, finished_at=timezone.now(),
                error="Worker stopped before this job finished. Submit a new job to retry.",
            )
            self.stdout.write("Collection worker started")
            try:
                while True:
                    job = CollectionJob.objects.filter(status=CollectionJob.Status.QUEUED).first()
                    if job is not None:
                        self.process(job, directory)
                    if options["once"]:
                        return
                    if job is None:
                        time.sleep(2)
            except KeyboardInterrupt:
                self.stdout.write("Collection worker stopped")

    def process(self, job: CollectionJob, directory: Path) -> None:
        """Run the shared pipeline in a child process with a timeout and log. / 공통 처리 흐름을 자식 프로세스에서 실행하고 시간 제한·로그를 적용합니다."""
        log_path = directory / f"{job.pk}.log"
        job.status = CollectionJob.Status.RUNNING
        job.started_at = timezone.now()
        job.log_path = str(log_path.relative_to(settings.BASE_DIR))
        job.save(update_fields=["status", "started_at", "log_path"])
        command = [sys.executable, "-u", "-m", "job_pipeline.cli",
                   "--source", "ats", "--search-limit", str(job.search_limit),
                   "--analyze-limit", str(job.analyze_limit), "--model", job.model]
        if job.discover:
            command.append("--discover")
        try:
            with log_path.open("w", encoding="utf-8") as log:
                completed = subprocess.run(command, cwd=settings.BASE_DIR,
                                           stdout=log, stderr=subprocess.STDOUT, timeout=1800)
            imported, invalid = import_analyses()
            if completed.returncode or invalid:
                job.status = CollectionJob.Status.FAILED
                job.error = f"Collection exited with code {completed.returncode}; invalid analyses: {invalid}. Check the worker log."
            else:
                job.status = CollectionJob.Status.COMPLETED
            self.stdout.write(f"Job {job.pk}: {job.status}; imported {imported}")
        except KeyboardInterrupt:
            job.status = CollectionJob.Status.FAILED
            job.error = "Collection interrupted. Submit a new job to retry."
            raise
        except Exception as error:
            job.status = CollectionJob.Status.FAILED
            job.error = str(error)
        finally:
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "finished_at"])
