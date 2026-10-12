"""Create the analysis table and collection queue. / 분석 테이블과 수집 작업 큐를 만듭니다."""
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="JobAnalysis", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("source_url", models.URLField(max_length=2048, unique=True)),
            ("title", models.CharField(max_length=500)),
            ("company", models.CharField(max_length=500)),
            ("location", models.CharField(max_length=500)),
            ("record", models.JSONField()),
            ("updated_at", models.DateTimeField(auto_now=True)),
        ], options={"ordering": ["-updated_at"]}),
        migrations.CreateModel(name="CollectionJob", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("status", models.CharField(choices=[("queued", "Queued"), ("running", "Running"), ("completed", "Completed"), ("failed", "Failed")], default="queued", max_length=16)),
            ("discover", models.BooleanField(default=False)),
            ("search_limit", models.PositiveIntegerField(default=5)),
            ("analyze_limit", models.PositiveIntegerField(default=1)),
            ("model", models.CharField(default="qwen3:8b", max_length=100)),
            ("error", models.TextField(blank=True)),
            ("log_path", models.TextField(blank=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("started_at", models.DateTimeField(blank=True, null=True)),
            ("finished_at", models.DateTimeField(blank=True, null=True)),
            ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
        ], options={"ordering": ["created_at"]}),
    ]
