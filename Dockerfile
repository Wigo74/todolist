FROM python:3.10.9-slim

WORKDIR /todolist

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install  -y --no-install-recommends gcc

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD python3 manage.py runserver 127.0.0.1:8000