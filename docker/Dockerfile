FROM python:3.12-alpine

# Don't generate .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# force unbuffered output
ENV PYTHONUNBUFFERED=1

LABEL app_name="Popcat Todo List"
LABEL description="Popcat Todo List is a Public Version of the Popcat Todo List"
LABEL version="1.0.0"
LABEL MAINTAINER="Herr Erde"

WORKDIR /app

COPY src/ .

RUN apt update && \
pip install --no-cache-dir --upgrade pip && \
pip install -r requirements.txt

CMD ["python", "main.py"]
