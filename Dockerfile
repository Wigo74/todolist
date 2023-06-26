FROM python:3.9.0-slim

# Устанавливает переменную окружения, которая гарантирует, что вывод из python будет отправлен прямо в терминал без предварительной буферизации
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

ADD requirements.txt /usr/src/app/requirements.txt
# Запускает команду pip install для всех библиотек, перечисленных в requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

# Устанавливает рабочий каталог контейнера — "code"
COPY . /usr/src/app
WORKDIR /usr/src/app

# Копирует все файлы из нашего локального проекта в контейнер
#COPY requirements.txt /app

# |ВАЖНЫЙ МОМЕНТ| копируем содержимое папки, где находится Dockerfile, в рабочую директорию контейнера
# если закоментировать то изменения в контейнере будут происходить срузу
COPY . /usr/src/app
ENTRYPOINT ["bash", "entrypoint.sh"]

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#FROM python:3.10.9-slim
#
#WORKDIR /todolist
#
#ENV PYTHONUNBUFFERED 1
#ENV PYTHONDONTWRITEBYTECODE 1
#
#RUN apt-get update && apt-get install  -y --no-install-recommends gcc
#
#COPY requirements.txt .
#
#RUN pip install --upgrade pip
#
#RUN pip install -r requirements.txt
#
#COPY . .
#ENTRYPOINT ['bash', 'entrypoint.sh']
#EXPOSE 8000
#
#CMD ['python3', 'manage.py', 'runserver', '0.0.0.0:8000']