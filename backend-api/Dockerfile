# Dockerfile.backend
FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

# 작업 디렉토리 설정
WORKDIR $APP_HOME

# 의존성 설치
COPY backend-api/requirements.txt $APP_HOME/requirements.txt
RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

# 애플리케이션 코드 복사
COPY backend-api/app $APP_HOME/app

# 포트 노출 (Kubernetes Service 포트와 일치)
EXPOSE 8000

# 컨테이너 시작 명령어
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]