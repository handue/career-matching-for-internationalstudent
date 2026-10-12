"""Persist analyses and worker status in Django's DB. / Django DB에 분석과 작업 상태를 저장합니다."""

import uuid
from django.conf import settings
from django.db import models


class JobAnalysis(models.Model):
    """Store validated saved analyses for the web. / 검증된 기존 분석을 웹 조회용으로 저장합니다."""
    source_url = models.URLField(max_length=2048, unique=True)
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=500)
    location = models.CharField(max_length=500)
    record = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]


class CollectionJob(models.Model):
    """Queue collection independently of HTTP requests. / HTTP 요청과 독립적으로 수집 작업을 등록합니다."""
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    discover = models.BooleanField(default=False)
    search_limit = models.PositiveIntegerField(default=5)
    analyze_limit = models.PositiveIntegerField(default=1)
    model = models.CharField(max_length=100, default="qwen3:8b")
    error = models.TextField(blank=True)
    log_path = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
