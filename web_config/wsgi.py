"""Expose Django to WSGI servers. / WSGI 서버에 Django를 연결합니다."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_config.settings")
application = get_wsgi_application()
