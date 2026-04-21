FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml README.md .
COPY wos_mvp ./wos_mvp
COPY tests ./tests
COPY runtime_data ./runtime_data
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "wos_mvp.app:app", "--host", "0.0.0.0", "--port", "8000"]
