# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     libpq-dev  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt ./requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY ./ ./

RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
