FROM python:3.10
WORKDIR /app
RUN apt-get update && apt-get install -y netcat-openbsd
COPY . /app/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
RUN python manage.py collectstatic --noinput
CMD ["sh", "-c", "python manage.py wait_for_db && python manage.py migrate && daphne -b 0.0.0.0 -p 8000 mytask.asgi:application"]