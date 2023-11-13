FROM python:3.9-slim

WORKDIR /app

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .
COPY video-convertor-402921-0a56b850480b.json /secrets/service-account-file.json

ENV GOOGLE_APPLICATION_CREDENTIALS /secrets/service-account-file.json

CMD ["python", "tasks.py"]

