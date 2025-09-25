# My Epic Loot — Backend (Django)

API service for the project. See `Makefile` for common tasks.

## Quickstart (Dev)

```bash
pip install -r backend/requirements-dev.txt
python backend/manage.py migrate
python backend/manage.py runserver
```

## Docker

```bash
docker build -t mel-backend -f backend/Dockerfile .
docker run --rm -p 8000:8000 mel-backend
```
