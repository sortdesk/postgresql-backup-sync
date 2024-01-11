FROM python:3.11-slim-bookworm
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y postgresql-client-15

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --user -r requirements.txt

RUN mkdir /backup

COPY app /app
WORKDIR /app

ENTRYPOINT ["python", "main.py", "schedule"]
