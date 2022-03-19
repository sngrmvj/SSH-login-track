FROM python:latest

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create working dir
WORKDIR /app

# install dependencies
RUN pip install --upgrade pip 
COPY client_wsgi.py /app/client_wsgi.py
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 5000