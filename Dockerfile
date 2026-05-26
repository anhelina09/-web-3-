FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py migrate && \
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.filter(phone='+380962652626').exists() or User.objects.create_superuser(phone='+380962652626', password='12345678')"

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]