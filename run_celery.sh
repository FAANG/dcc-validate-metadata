python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
celery -A metadata_validation_conversion worker -l INFO -Q conversion,validation,submission,upload,update,graphql_api,gsearch