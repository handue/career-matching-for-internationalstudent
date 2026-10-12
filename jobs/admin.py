"""Inspect analyses and worker runs through Django admin. / Django 관리자에서 분석과 작업을 조회합니다."""
from django.contrib import admin
from .models import CollectionJob, JobAnalysis

admin.site.register(JobAnalysis)
admin.site.register(CollectionJob)
