# Dockerfile.translate
FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

WORKDIR $APP_HOME

COPY translate-service/requirements.txt $APP_HOME/requirements.txt
RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

COPY translate-service/app/translate_app.py $APP_HOME/app/
#COPY translate-service/app/__init__.py $APP_HOME/app/

EXPOSE 8002

CMD ["uvicorn", "app.translate_app:app", "--host", "0.0.0.0", "--port", "8002"]