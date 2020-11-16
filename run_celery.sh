python manage.py migrate
celery -A metadata_validation_conversion worker -l INFO -Q conversion,validation,submission,upload