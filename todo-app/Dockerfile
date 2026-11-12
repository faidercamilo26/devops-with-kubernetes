FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=3000

WORKDIR /app

COPY app.py .

USER nobody

EXPOSE 3000

CMD ["python", "app.py"]
