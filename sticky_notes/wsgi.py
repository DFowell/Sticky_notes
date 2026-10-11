"""WSGI config for sticky_notes."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sticky_notes.settings")
application = get_wsgi_application()
