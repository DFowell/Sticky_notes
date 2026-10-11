"""Main URL configuration for sticky_notes."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Include the notes app's URLs at the site root (Step 8)
    path("", include("notes.urls")),
]
