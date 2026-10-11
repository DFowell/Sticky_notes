"""ASGI config for sticky_notes."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sticky_notes.settings")
application = get_asgi_application()
