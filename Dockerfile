# Используем базовый образ Python
FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем и устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY Pipfile Pipfile.lock /app/

# Устанавливаем зависимости
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

# Копируем код в контейнер
COPY . /app/

# Создаем миграции
RUN pipenv run python manage.py makemigrations

# Выполняем миграции
RUN pipenv run python manage.py migrate

# Открываем порт, на котором будет работать Django
EXPOSE 8000

# Запускаем Django приложение без автоматической перезагрузки
CMD ["pipenv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]