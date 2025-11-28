FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV FAISS_INDEX_PATH /app/data/kfood_faiss.index
ENV METADATA_PATH /app/data/kfood_metadata.json

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.faiss_utils:app", "--host", "0.0.0.0", "--port", "8000"]