FROM python:3.9.7
ADD metadata_validation_conversion metadata_validation_conversion
WORKDIR metadata_validation_conversion
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc &&\
    chmod +x mc
ADD requirements.txt ./
ADD run_daphne.sh ./
ADD run_celery.sh ./
ADD run_flower.sh ./
RUN pip install -r requirements.txt
RUN pip install --upgrade awscli
ENV PYTHONUNBUFFERED=1