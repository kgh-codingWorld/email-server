# Email Server (FastAPI + Redis)

이 프로젝트는 홈페이지에서 사용자가 이메일을 작성하면, 이를 담당자에게 전송하는 **비동기 이메일 처리 서버**입니다. 

---

## 주요 특징

- ✅ **FastAPI 기반** RESTful API 서버
- ✅ **Redis 큐 기반 비동기 처리**
- ✅ **SMTP 이메일 전송 (TLS 보안)**
- ✅ **3회 재시도 후 실패 처리**
- ✅ **Polling 방식으로 처리 결과 확인 가능**

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| Language | Python 3.11.9 |
| Framework | FastAPI |
| Queue | Redis (via `redis.asyncio`) |
| Email | `aiosmtplib` + SMTP |
| Logging | Python `logging` 모듈 |
| Test | `pytest`, `TestClient` |

---

## 실행 방법

### 1. Redis 실행 (Docker 기반)

```bash
docker run -d --name redis-server -p 6379:6379 redis
```

### 2. FastAPI 서버 실행

```bash
uvicorn server.main:app --reload
```

### 3. Swagger 접속

```
http://localhost:8000/docs
```

---

## 이메일 전송 흐름

1. 사용자가 `/api/v1/email/received`로 이메일 전송 요청
2. 서버는 `task_id` 생성 후 Redis 큐(`email_queue`)에 등록
3. 백그라운드 워커가 큐에서 요청 꺼내 전송 시도 (최대 3회)
4. 상태(`pending`, `success`, `failed`)는 Redis에 저장됨
5. 클라이언트는 `/result?task_id=...`를 polling하여 전송 결과 확인

---

## API 명세

### 1. 이메일 전송 요청 (POST)
```
POST /api/v1/email/received
```
#### Body (JSON)
```json
{
  "to": "user@example.com",
  "subject": "Hello",
  "body": "{username}님 안녕하세요!",
  "username": "홍길동"
}
```
#### Response
```json
{
  "task_id": "uuid-value",
  "status": "queued"
}
```

### 2. 전송 결과 조회 (GET)
```
GET /api/v1/email/result?task_id=<TASK_ID>
```
#### Response 예시
- 처리 중:
```json
{
  "status": "pending",
  "to": "user@example.com"
}
```
- 성공:
```json
{
  "status": "success",
  "to": "user@example.com",
  "attempts": 1
}
```
- 실패:
```json
{
  "status": "failed",
  "to": "user@example.com",
  "reason": "전송 3회 실패",
  "attempts": 3
}
```

---

## 성능 테스트

`tests/performance/test_email_send_time.py`를 통해 단건 및 다건 테스트 수행 가능

```bash
pytest -m performance
```

---

## 폴더 구조

```
server/
├── configs/
│   └── lifespan.py
├── error/
│   └── email_exception_handler.py
├── log/
│   └── logger.py
├── models/
│   └── email_DTO.py
├── routes/
│   ├── email_receiver.py
│   └── email_result.py
├── utils/
│   ├── email_util.py
│   └── worker_util.py
└── main.py
```

---

## 비고

- Redis가 실행되지 않으면 워커에서 예외 발생
- 이메일 전송 실패 시 로그에 사유 기록
- 이후 Redis → Celery 구조로 확장 가능

---

## 개발자 가이드

### .env 예시
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```
