release: python manage.py makemigrations && python manage.py migrate

web: gunicorn habit_api.wsgi
