# Service CRM

Python CRM для сервисного центра на FastAPI.

## Что будет в CRM

- заказы и ремонты;
- клиенты;
- инженеры;
- статусы ремонта;
- склад деталей;
- зарплаты;
- Telegram-уведомления;
- веб-интерфейс на домене `crm-fadeev.ru`.

## Технологии

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite на старте, PostgreSQL позже
- Jinja2 templates
- Uvicorn

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Открыть:

```text
http://127.0.0.1:8000
```

## Структура

```text
service-crm/
├─ app/
│  ├─ main.py
│  ├─ database.py
│  ├─ models.py
│  ├─ templates/
│  │  └─ dashboard.html
│  └─ static/
│     └─ style.css
├─ requirements.txt
└─ README.md
```
