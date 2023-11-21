FROM python:3.9-slim

WORKDIR /app
COPY . /app
COPY video-convertor-402921-0a56b850480b.json /secrets/service-account-file.json

RUN pip install --upgrade pip && \
    pip install -r requirements.txt gunicorn

RUN mkdir -p /app/videos/uploaded
RUN mkdir -p /app/videos/converted

ENV GOOGLE_APPLICATION_CREDENTIALS /secrets/service-account-file.json

EXPOSE 5000

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
