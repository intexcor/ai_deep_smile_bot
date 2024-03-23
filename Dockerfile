FROM python:3.12

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install -r requirements.txt

COPY srs /app/srs
COPY .env /app/.env
CMD ["python", "srs/main.py"]