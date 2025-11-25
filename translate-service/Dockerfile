FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV APP_HOME /app

WORKDIR $APP_HOME

# 1. [수정] 경로에서 'translate-service/' 제거
# context가 이미 해당 폴더 내부이기 때문입니다.
COPY requirements.txt $APP_HOME/requirements.txt
RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

# 2. [수정] 소스 코드 복사 경로 수정
# 파일 하나만 복사하기보다 app 폴더 전체를 복사하는 것이 관리하기 편합니다.
COPY app/ $APP_HOME/app/

# 3. [수정] 포트 번호 8000으로 변경
# docker-compose가 내부 포트 8000을 바라보고 있습니다.
EXPOSE 8000

# 실행 명령어 포트도 8000으로 변경
CMD ["uvicorn", "app.translate_app:app", "--host", "0.0.0.0", "--port", "8000"]