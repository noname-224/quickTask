FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT="/usr/local"

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY ./src ./src

ENV PYTHONPATH=/app/src

CMD ["python", "src/main.py"]
