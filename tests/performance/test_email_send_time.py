import time
import asyncio
import pytest
from fastapi.testclient import TestClient # FastAPI + TestClient를 사용하려면 내부적으로 httpx 라이브러리가 있어야 한다.
from server.main import app
from server.log.logger import logger

client = TestClient(app)

@pytest.mark.performance
def test_single_email_send_time():
    """단건 이메일 전송 요청 시간 측정"""
    payload = {
        "to": "kildong@example.com",
        "subject": "단건 테스트",
        "body": "이메일 본문입니다.",
        "username": "길동이"
    }

    start = time.perf_counter()
    response = client.post("/api/v1/email/received", json=payload)
    end = time.perf_counter()

    elaspsed = round(end - start, 4)
    logger.info(f"\n 단건 요청 시간: {elaspsed}초")

    assert response.status_code == 200
    assert "task_id" in response.json()
    assert elaspsed < 1.0


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_email_requests():
    """다건 동시 이메일 전송 요청 시간 측정"""
    NUM_REQUESTS = 5

    async def send_email(i):
        payload = {
            "to": f"user{i}@example.com",
            "subject": f"Test {i}",
            "body": f"Hello User {i}",
            "username": f"User{i}"
        }

        loop = asyncio.get_event_loop()
        start = time.perf_counter()
        response = await loop.run_in_executor(
            None, 
            lambda: client.post("/api/v1/email/received", json=payload))
        end = time.perf_counter()
        elapsed = round(end - start, 4)
        logger.info(f"user{i} 요청 완료 - {elapsed}초")

        assert response.status_code == 200
        return elapsed

    start_all = time.perf_counter()
    results = await asyncio.gather(*(send_email(i) for i in range(NUM_REQUESTS)))
    end_all = time.perf_counter()

    total_elapsed = round(end_all - start_all, 4)
    logger.info(f"\n 총 {NUM_REQUESTS}건 동시 요청 시간: {total_elapsed}초")

    assert total_elapsed < 3.0