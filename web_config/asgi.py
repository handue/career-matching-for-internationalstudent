"""Expose Django to ASGI servers. / ASGI 서버에 Django를 연결합니다."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_config.settings")
application = get_asgi_application()
