# Sticky Notes (Django)

A simple Django app for creating, viewing, editing and deleting sticky notes.

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations   # should say "No changes detected"
python manage.py migrate
python manage.py collectstatic    # copies CSS into ./staticfiles
python manage.py test             # optional: runs the CRUD tests
python manage.py runserver
```

Open http://127.0.0.1:8000/

## URLs

| URL                  | Purpose            |
|----------------------|--------------------|
| `/`                  | List all notes     |
| `/create/`           | Create a note      |
| `/<id>/`             | View a note        |
| `/<id>/edit/`        | Edit a note        |
| `/<id>/delete/`      | Delete a note      |
| `/admin/`            | Django admin       |

## Diagrams

See the `diagrams/` folder: use case, sequence (create + delete) and class diagrams as PNG images, plus editable `.drawio` files (open at https://app.diagrams.net).

## Testing

Run `python manage.py test`. See `TESTING.md` for the automated test summary and the manual testing checklist.
