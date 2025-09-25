# My Epic Loot — Backend (Django)

API service for the project. See `Makefile` for common tasks.

## Quickstart (Dev)

```bash
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

## Docker

```bash
docker build -t mel-backend -f Dockerfile .
docker run --rm -p 8000:8000 mel-backend
```
