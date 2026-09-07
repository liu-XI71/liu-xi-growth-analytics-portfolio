FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin appuser
COPY --chown=appuser:appuser pyproject.toml ./
COPY --chown=appuser:appuser analytics ./analytics
COPY --chown=appuser:appuser backend ./backend
COPY --chown=appuser:appuser scripts ./scripts
COPY --chown=appuser:appuser sql ./sql
COPY --chown=appuser:appuser data ./data
RUN pip install --upgrade pip && pip install .
RUN mkdir -p /app/data/demo && chown -R appuser:appuser /app/data

EXPOSE 8000
USER appuser
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
