    SunLite Full Project (Backend + Bot)

    Quickstart (local):

1) Create virtualenv and install requirements

    python -m venv venv
    venv\Scripts\activate   # Windows
    pip install -r requirements.txt

2) Backend (Django):

    cd backend
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

    Backend API will be at http://127.0.0.1:8000/api/

3) Bot:

    cd bot
    copy ..\.env.example .env   # and fill BOT_TOKEN
    python -m venv venv
    venv\Scripts\activate
    pip install -r ../requirements.txt
    python main.py

Notes:
- This project uses SQLite for local testing.
- Admin username default is @mr1kevin in .env.example
