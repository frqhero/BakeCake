#!/bin/sh
/app/backend/manage.py run_bot &
gunicorn backend.wsgi:application --bind 0:8000

