FROM python:3.12-slim

WORKDIR /app
COPY --chown=10001:10001 app.py .

USER 10001
EXPOSE 8000
CMD ["python", "app.py"]
