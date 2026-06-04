# SECURITY: Python 3.9 reached end-of-life (2025-10). 3.9.21 is the latest 3.9
# patch; plan a migration to a supported runtime (3.12+). Also consider adding a
# non-root USER once volume ownership for /data and the nginx files dir is set.
FROM python:3.9.21
ADD metadata_validation_conversion metadata_validation_conversion
WORKDIR metadata_validation_conversion
ADD requirements.txt ./
ADD run_uvicorn.sh ./
ADD run_celery.sh ./
ADD run_flower.sh ./
RUN pip install -r requirements.txt
RUN pip install --upgrade awscli
ENV PYTHONUNBUFFERED=1
