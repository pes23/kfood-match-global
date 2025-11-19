# Dockerfile.faiss
FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

# PV/PVC 사용 불가 시 인덱스 파일 경로를 컨테이너 내부 경로로 설정
# faiss_utils.py는 이 환경 변수를 사용하거나 기본값(/mnt/data)을 사용.
ENV FAISS_INDEX_PATH /mnt/data/kfood_faiss.index
ENV METADATA_PATH /mnt/data/kfood_metadata.json

WORKDIR $APP_HOME

COPY faiss/requirements.txt $APP_HOME/requirements.txt
RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

# 인덱스 파일과 메타데이터를 COPY할 준비 (PV 사용 불가 대비)
# PV 사용 실패 시 이 파일들을 수동으로 이미지에 빌드해야 합니다.
COPY faiss/data/kfood_faiss.index $APP_HOME/data/kfood_faiss.index
COPY faiss/data/kfood_metadata.json $APP_HOME/data/kfood_metadata.json

COPY faiss/app $APP_HOME/app

# 포트 노출 (내부 ClusterIP Service 포트)
EXPOSE 8001

CMD ["uvicorn", "app.faiss_utils:app", "--host", "0.0.0.0", "--port", "8001"]