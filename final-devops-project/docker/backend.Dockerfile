FROM python:3.12-alpine AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apk upgrade --no-cache
COPY application/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY application/backend/app ./app
COPY application/backend/alembic ./alembic
COPY application/backend/alembic.ini ./
RUN addgroup -g 10001 taskboard && adduser -D -H -u 10001 -G taskboard taskboard

FROM base AS test
COPY application/backend/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY application/backend/tests ./tests
USER 10001:10001
CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]

FROM base AS runtime
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
