FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

WORKDIR $APP_HOME

COPY requirements.txt $APP_HOME/requirements.txt
RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

COPY app/ $APP_HOME/app/

EXPOSE 8000

CMD ["uvicorn", "app.translate_app:app", "--host", "0.0.0.0", "--port", "8001"]