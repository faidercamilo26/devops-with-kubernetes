FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /usr/src/app

COPY app.py .

USER nobody

EXPOSE 8080

CMD ["python", "app.py"]
