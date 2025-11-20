FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 1. [중요] Context 경로 수정
# 이미 faiss 폴더 내부이므로 'faiss/' 접두사를 제거해야 합니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 환경 변수 및 데이터 경로 설정
# docker-compose.yml에서 볼륨을 '/app/data'로 마운트하므로 경로를 맞춰줍니다.
# /mnt/data 대신 /app/data를 사용하는 것이 관리하기 편합니다.
ENV FAISS_INDEX_PATH /app/data/kfood_faiss.index
ENV METADATA_PATH /app/data/kfood_metadata.json

# 3. 데이터 파일 복사 (선택 사항)
# 로컬 개발 시에는 Volume이 덮어씌우지만, 배포를 위해 이미지를 구울 때 포함시킵니다.
# (주의: 로컬 faiss/data 폴더에 실제 파일이 있어야 에러가 안 납니다.)
# COPY data/ ./data/

# 4. 앱 코드 복사
# 'faiss/app'이 아니라 'app/'으로 수정
COPY app/ ./app/

# 5. [중요] 포트 번호 수정 (8001 -> 8000)
# docker-compose가 내부 포트 8000을 바라보고 있습니다.
EXPOSE 8000

# 실행 명령어의 포트도 8000으로 변경
CMD ["uvicorn", "app.faiss_utils:app", "--host", "0.0.0.0", "--port", "8000"]