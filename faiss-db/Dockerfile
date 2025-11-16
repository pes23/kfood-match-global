# Dockerfile.faiss
FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app
# PV/PVC가 마운트될 경로를 ENV 변수로 지정하여 코드에서 참조
ENV FAISS_DATA_PATH /mnt/data/kfood_faiss_index.bin

WORKDIR $APP_HOME
# pv 사용 못할 경우 인덱스 파일을 이미지에 포함시킵니다.
COPY faiss-db/data/kfood_faiss_index.bin $APP_HOME/data/
COPY faiss-db/app/metadata.json $APP_HOME/data/

# FAISS는 numpy에 의존, FAISS 자체는 faiss-cpu를 설치
COPY faiss-db/requirements.txt $APP_HOME/requirements.txt
RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

# FAISS DB API 로직 및 메타데이터 파일을 복사
COPY faiss-db/app/faiss_utils.py $APP_HOME/app/
COPY faiss-db/app/metadata.json $APP_HOME/app/

# 포트 노출 (내부 ClusterIP Service 포트)
EXPOSE 8001

# 컨테이너 시작 명령어
CMD ["uvicorn", "app.faiss_utils:app", "--host", "0.0.0.0", "--port", "8001"]