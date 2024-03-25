FROM python:3-alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /app
CMD ["python3", "solarman2timescaledb.py"]
RUN apk add -U libpq
COPY requirements.txt requirements.txt
RUN apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev \
    && pip install -r requirements.txt \
    && apk del build-deps
COPY . /app/