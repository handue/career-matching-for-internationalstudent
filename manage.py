"""Run Django management commands. / Django 관리 명령을 실행합니다."""

import os
import sys


def main() -> None:
    """Select Django settings and run the CLI. / Django 설정을 선택하고 명령을 실행합니다."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
