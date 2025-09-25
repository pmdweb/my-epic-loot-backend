#!/bin/bash
set -e

echo "✅ Running database migrations..."
python manage.py migrate --noinput

if [ "${DJANGO_COLLECTSTATIC:-0}" = "1" ]; then
  echo "✅ Collecting static files..."
  python manage.py collectstatic --noinput
else
  echo "⏭️  Skipping collectstatic (DJANGO_COLLECTSTATIC!=1)"
fi

echo "✅ Starting Gunicorn..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000
