FROM python:3.12-alpine

# Don't generate .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# force unbuffered output
ENV PYTHONUNBUFFERED=1

LABEL app_name="Popcat Bot"
LABEL description="Popcat Bot is a Public Version of the Popcat Discord Bot"
LABEL version="0.0.1"
LABEL MAINTAINER="Herr Erde"

WORKDIR /app

COPY src/ .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
