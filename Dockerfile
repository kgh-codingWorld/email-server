# base 이미지 선택
FROM python:3.11-slim

# 작업 디렉토리 생성
WORKDIR /app

# 종속성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 소스 복사
COPY . .

# 포트 오픈
EXPOSE 8000

# 앱 실행 (uvicorn 사용)
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
