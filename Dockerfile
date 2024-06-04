FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /healthapp
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python manage.py runserver 0.0.0.0:80