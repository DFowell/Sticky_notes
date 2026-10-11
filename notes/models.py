from django.db import models
from django.urls import reverse


class Note(models.Model):
    """A single sticky note."""

    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]  # most recently edited first

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("notes:detail", kwargs={"pk": self.pk})
