from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import NoteForm
from .models import Note


class NoteListView(ListView):
    """READ (all): show every note."""

    model = Note
    template_name = "notes/note_list.html"
    context_object_name = "notes"


class NoteDetailView(DetailView):
    """READ (one): show a single note."""

    model = Note
    template_name = "notes/note_detail.html"
    context_object_name = "note"


class NoteCreateView(CreateView):
    """CREATE: add a new note."""

    model = Note
    form_class = NoteForm
    template_name = "notes/note_form.html"
    success_url = reverse_lazy("notes:list")

    def form_valid(self, form):
        messages.success(self.request, "Note created.")
        return super().form_valid(form)


class NoteUpdateView(UpdateView):
    """UPDATE: edit an existing note."""

    model = Note
    form_class = NoteForm
    template_name = "notes/note_form.html"
    success_url = reverse_lazy("notes:list")

    def form_valid(self, form):
        messages.success(self.request, "Note updated.")
        return super().form_valid(form)


class NoteDeleteView(DeleteView):
    """DELETE: remove a note after confirmation."""

    model = Note
    template_name = "notes/note_confirm_delete.html"
    context_object_name = "note"
    success_url = reverse_lazy("notes:list")

    def form_valid(self, form):
        messages.success(self.request, "Note deleted.")
        return super().form_valid(form)
