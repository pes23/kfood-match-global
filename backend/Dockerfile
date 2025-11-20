FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV APP_HOME /app

WORKDIR $APP_HOME

# 1. pip 업그레이드 (필수)
RUN pip install --no-cache-dir --upgrade pip

# 2. [핵심] PyTorch CPU 버전 먼저 설치 (용량 절약 & 에러 방지)
# requirements.txt에 넣으면 GPU 버전을 받아버려 용량이 터질 수 있습니다.
#RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

# 3. Sentence Transformers 설치
# 위에서 설치한 torch(CPU)를 인식하여 재설치하지 않습니다.
#RUN pip install --no-cache-dir sentence-transformers

# 4. 나머지 일반 패키지 설치 (requirements.txt)
COPY requirements.txt $APP_HOME/requirements.txt
RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

# 5. 소스 코드 복사
COPY app $APP_HOME/app

EXPOSE 8000

# 실행
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]