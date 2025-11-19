# Dockerfile.backend
FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

WORKDIR $APP_HOME

COPY backend/requirements.txt $APP_HOME/requirements.txt
RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

COPY backend/app $APP_HOME/app

EXPOSE 8000

# K8s Secret을 통해 주입된 GEMINI_API_KEY 환경 변수를 사용하여 실행.
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]