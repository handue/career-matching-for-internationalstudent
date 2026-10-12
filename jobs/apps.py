from django.apps import AppConfig


class JobsConfig(AppConfig):
    """Register the jobs app with Django. / Django에 jobs 앱을 등록합니다."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobs"
