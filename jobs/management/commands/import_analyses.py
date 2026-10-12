"""Import existing files through Django CLI. / Django 명령으로 기존 파일을 가져옵니다."""
from django.core.management.base import BaseCommand
from jobs.services import import_analyses


class Command(BaseCommand):
    help = "Import validated saved job analyses into the database."

    def handle(self, *args: object, **options: object) -> None:
        imported, failed = import_analyses()
        self.stdout.write(f"Imported: {imported}, invalid files skipped: {failed}")
