python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
uvicorn --host 0.0.0.0 --port 8000 metadata_validation_conversion.asgi:application --workers=6