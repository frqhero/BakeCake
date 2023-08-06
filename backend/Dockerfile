#!/bin/bash
FROM python:3.10.4

WORKDIR /app

COPY requirements.txt /app


RUN pip install -r /app/requirements.txt --no-cache-dir

COPY ./ ./
# RUN chmod +x /entrypoint.sh

WORKDIR backend

# CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]
ENTRYPOINT ["/app/backend/entrypoint.sh"]
# CMD ["./app/"]