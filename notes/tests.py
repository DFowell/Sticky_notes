"""Unit tests for the notes app, grouped by the use case they cover."""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from . import views
from .forms import NoteForm
from .models import Note


def make_note(title="Shopping", content="Buy milk and eggs"):
    """Create and return a saved note."""
    return Note.objects.create(title=title, content=content)


class UrlTests(TestCase):
    """URL patterns map to the right views."""

    def test_urls_resolve_to_expected_views(self):
        self.assertEqual(resolve("/").func.view_class, views.NoteListView)
        self.assertEqual(
            resolve("/create/").func.view_class, views.NoteCreateView
        )
        self.assertEqual(resolve("/1/").func.view_class, views.NoteDetailView)
        self.assertEqual(
            resolve("/1/edit/").func.view_class, views.NoteUpdateView
        )
        self.assertEqual(
            resolve("/1/delete/").func.view_class, views.NoteDeleteView
        )

    def test_reverse_builds_expected_paths(self):
        self.assertEqual(reverse("notes:list"), "/")
        self.assertEqual(reverse("notes:create"), "/create/")
        self.assertEqual(reverse("notes:detail", args=[5]), "/5/")
        self.assertEqual(reverse("notes:update", args=[5]), "/5/edit/")
        self.assertEqual(reverse("notes:delete", args=[5]), "/5/delete/")


class NoteModelTests(TestCase):
    """The Note model stores and validates data correctly."""

    def test_str_returns_title(self):
        self.assertEqual(str(make_note("My title")), "My title")

    def test_get_absolute_url(self):
        note = make_note()
        self.assertEqual(note.get_absolute_url(), f"/{note.pk}/")

    def test_timestamps_are_set_on_create(self):
        note = make_note()
        self.assertIsNotNone(note.created_at)
        self.assertIsNotNone(note.updated_at)

    def test_saving_keeps_created_at_and_advances_updated_at(self):
        note = make_note()
        created, first_update = note.created_at, note.updated_at
        note.content = "Changed"
        note.save()
        note.refresh_from_db()
        self.assertEqual(note.created_at, created)
        self.assertGreaterEqual(note.updated_at, first_update)

    def test_notes_ordered_most_recently_updated_first(self):
        older = make_note("Older")
        newer = make_note("Newer")
        Note.objects.filter(pk=older.pk).update(
            updated_at=timezone.now() - timedelta(days=1)
        )
        self.assertEqual(list(Note.objects.all()), [newer, older])

    def test_title_longer_than_100_characters_is_invalid(self):
        note = Note(title="x" * 101, content="Content")
        with self.assertRaises(ValidationError):
            note.full_clean()

    def test_blank_title_and_content_are_invalid(self):
        with self.assertRaises(ValidationError):
            Note(title="", content="Content").full_clean()
        with self.assertRaises(ValidationError):
            Note(title="Title", content="").full_clean()


class NoteFormTests(TestCase):
    """The form validates user input."""

    def test_form_only_exposes_title_and_content(self):
        self.assertEqual(list(NoteForm().fields), ["title", "content"])

    def test_valid_data_is_accepted_and_saved(self):
        form = NoteForm({"title": "Title", "content": "Content"})
        self.assertTrue(form.is_valid())
        note = form.save()
        self.assertEqual(Note.objects.get(pk=note.pk).title, "Title")

    def test_missing_title_is_rejected(self):
        form = NoteForm({"title": "", "content": "Content"})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_missing_content_is_rejected(self):
        form = NoteForm({"title": "Title", "content": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_title_too_long_is_rejected(self):
        form = NoteForm({"title": "x" * 101, "content": "Content"})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)


class ListNotesTests(TestCase):
    """Use case: view all notes."""

    def test_page_loads_with_correct_templates(self):
        response = self.client.get(reverse("notes:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_list.html")
        self.assertTemplateUsed(response, "notes/base.html")

    def test_empty_state_is_shown_when_there_are_no_notes(self):
        response = self.client.get(reverse("notes:list"))
        self.assertContains(response, "You have no notes yet.")
        self.assertEqual(len(response.context["notes"]), 0)

    def test_existing_notes_are_listed(self):
        make_note("First", "Alpha")
        make_note("Second", "Beta")
        response = self.client.get(reverse("notes:list"))
        self.assertContains(response, "First")
        self.assertContains(response, "Second")
        self.assertNotContains(response, "You have no notes yet.")

    def test_most_recently_updated_note_comes_first(self):
        older = make_note("Older")
        newer = make_note("Newer")
        Note.objects.filter(pk=older.pk).update(
            updated_at=timezone.now() - timedelta(days=1)
        )
        response = self.client.get(reverse("notes:list"))
        self.assertEqual(list(response.context["notes"]), [newer, older])

    def test_long_content_is_truncated_in_the_list(self):
        words = " ".join(f"tok{i}x" for i in range(60))
        make_note("Long", words)
        response = self.client.get(reverse("notes:list"))
        self.assertContains(response, "tok0x")
        self.assertNotContains(response, "tok59x")

    def test_html_in_notes_is_escaped(self):
        make_note("<b>bold</b>", "Body")
        response = self.client.get(reverse("notes:list"))
        self.assertNotContains(response, "<b>bold</b>")
        self.assertContains(response, "&lt;b&gt;bold&lt;/b&gt;")


class ViewNoteTests(TestCase):
    """Use case: view a single note."""

    def test_detail_page_shows_the_note(self):
        note = make_note("Meeting", "Agenda for Monday")
        response = self.client.get(note.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_detail.html")
        self.assertContains(response, "Meeting")
        self.assertContains(response, "Agenda for Monday")
        self.assertEqual(response.context["note"], note)

    def test_missing_note_returns_404(self):
        response = self.client.get(reverse("notes:detail", args=[9999]))
        self.assertEqual(response.status_code, 404)


class CreateNoteTests(TestCase):
    """Use case: create a note."""

    def test_form_page_loads(self):
        response = self.client.get(reverse("notes:create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_form.html")
        self.assertIsInstance(response.context["form"], NoteForm)

    def test_valid_post_creates_note_and_redirects_to_list(self):
        response = self.client.post(
            reverse("notes:create"), {"title": "New", "content": "Body"}
        )
        self.assertRedirects(response, reverse("notes:list"))
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, "New")
        self.assertEqual(note.content, "Body")

    def test_success_message_is_shown(self):
        response = self.client.post(
            reverse("notes:create"),
            {"title": "New", "content": "Body"},
            follow=True,
        )
        self.assertContains(response, "Note created.")

    def test_invalid_post_does_not_create_note(self):
        response = self.client.post(
            reverse("notes:create"), {"title": "", "content": ""}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 0)
        self.assertFormError(
            response.context["form"], "title", "This field is required."
        )
        self.assertFormError(
            response.context["form"], "content", "This field is required."
        )


class EditNoteTests(TestCase):
    """Use case: edit a note."""

    def setUp(self):
        self.note = make_note("Original", "Original body")
        self.url = reverse("notes:update", args=[self.note.pk])

    def test_form_is_prefilled_with_existing_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_form.html")
        self.assertEqual(response.context["form"].instance, self.note)
        self.assertEqual(response.context["form"]["title"].value(), "Original")

    def test_valid_post_updates_note_and_redirects(self):
        response = self.client.post(
            self.url, {"title": "Edited", "content": "Edited body"}
        )
        self.assertRedirects(response, reverse("notes:list"))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Edited")
        self.assertEqual(self.note.content, "Edited body")

    def test_editing_does_not_create_a_second_note(self):
        self.client.post(self.url, {"title": "Edited", "content": "Body"})
        self.assertEqual(Note.objects.count(), 1)

    def test_success_message_is_shown(self):
        response = self.client.post(
            self.url, {"title": "Edited", "content": "Body"}, follow=True
        )
        self.assertContains(response, "Note updated.")

    def test_invalid_post_leaves_note_unchanged(self):
        response = self.client.post(self.url, {"title": "", "content": "x"})
        self.assertEqual(response.status_code, 200)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Original")

    def test_missing_note_returns_404(self):
        response = self.client.get(reverse("notes:update", args=[9999]))
        self.assertEqual(response.status_code, 404)


class DeleteNoteTests(TestCase):
    """Use case: delete a note (with confirmation)."""

    def setUp(self):
        self.note = make_note("Temporary", "Delete me")
        self.url = reverse("notes:delete", args=[self.note.pk])

    def test_get_shows_confirmation_and_does_not_delete(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_confirm_delete.html")
        self.assertContains(response, "Delete this note?")
        self.assertEqual(Note.objects.count(), 1)

    def test_post_deletes_note_and_redirects(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("notes:list"))
        self.assertEqual(Note.objects.count(), 0)

    def test_success_message_is_shown(self):
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, "Note deleted.")

    def test_only_the_chosen_note_is_deleted(self):
        other = make_note("Keep me", "Stay")
        self.client.post(self.url)
        self.assertEqual(list(Note.objects.all()), [other])

    def test_missing_note_returns_404(self):
        response = self.client.post(reverse("notes:delete", args=[9999]))
        self.assertEqual(response.status_code, 404)


class FullWorkflowTests(TestCase):
    """End-to-end: create, read, update and delete in one flow."""

    def test_complete_crud_workflow(self):
        response = self.client.post(
            reverse("notes:create"),
            {"title": "Plan", "content": "Draft"},
            follow=True,
        )
        self.assertContains(response, "Plan")
        note = Note.objects.get(title="Plan")

        response = self.client.get(note.get_absolute_url())
        self.assertContains(response, "Draft")

        response = self.client.post(
            reverse("notes:update", args=[note.pk]),
            {"title": "Plan v2", "content": "Final"},
            follow=True,
        )
        self.assertContains(response, "Plan v2")

        response = self.client.post(
            reverse("notes:delete", args=[note.pk]), follow=True
        )
        self.assertContains(response, "You have no notes yet.")
        self.assertEqual(Note.objects.count(), 0)
