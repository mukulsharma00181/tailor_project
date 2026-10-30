MANOJ SHARMA TAILOR SHOP - Django project

FIRST TIME SETUP (run inside this tailor_project folder, where manage.py is)

Windows (Command Prompt / VS Code terminal):
    py -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py makemigrations shop
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Mac / Linux:
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py makemigrations shop
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

NEXT TIMES (only):
    venv\Scripts\activate        (Mac/Linux: source venv/bin/activate)
    python manage.py runserver

OPEN IN BROWSER
    Public page  : http://127.0.0.1:8000/
    Owner login  : http://127.0.0.1:8000/login/
    Orders (CRUD): http://127.0.0.1:8000/orders/
    Django admin : http://127.0.0.1:8000/admin/

Database: SQLite file db.sqlite3 (created automatically by "migrate").
