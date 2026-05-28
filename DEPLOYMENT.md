# Deployment Guide

## Production stack

- Ubuntu 22.04
- Python 3.11+
- PostgreSQL
- Gunicorn
- Nginx
- SSL (Let's Encrypt)

## Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run migrations

```bash
python manage.py migrate
```

## Collect static

```bash
python manage.py collectstatic
```

## Run server

```bash
gunicorn config.wsgi:application
```
