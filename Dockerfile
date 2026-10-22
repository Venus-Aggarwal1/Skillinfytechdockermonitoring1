FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached between code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# main:app = file main.py, object named app. Must bind 0.0.0.0 so Prometheus can reach it.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
