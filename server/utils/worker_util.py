import asyncio
import json
from redis.asyncio import Redis
from server.log.logger import logger
from server.utils.email_util import preprocess_email, send_email_async

# Redis 연결
redis = Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Redis 키 상수
EMAIL_QUEUE = "email_queue"
TASK_RESULT_PREFIX = "task_status:"

# 이메일 전송 워커
async def email_worker():
    """이메일 전송 워커 함수"""
    while True:
        try:
            task = await redis.blpop(EMAIL_QUEUE, timeout=5)
            if not task:
                continue

            # 비동기 큐에서 정보 가져옴
            _, raw_data = task
            email_data = json.loads(raw_data)
            task_id = email_data["task_id"]
            retry_cnt = 0

            logger.info(f"{task_id} 이메일 전송 요청 수신")
            logger.info(f"{email_data['to']}에게 이메일 전송 시작")

            # 전처리
            email_data = preprocess_email(email_data)
            logger.debug(f"전처리 결과: {email_data}")

            # 3회 재시도
            while retry_cnt < 3:
                try:
                    retry_cnt += 1
                    logger.info(f"{task_id} 전송 재시도 {retry_cnt}회차")

                    await send_email_async(
                        email_data["to"],
                        email_data["subject"],
                        email_data["body"],
                        email_data["username"]
                    )

                    logger.info(f"{email_data['to']} 전송 성공")
                    await redis.set(
                        TASK_RESULT_PREFIX + task_id,
                        json.dumps({
                            "status":"success",
                            "to":email_data["to"],
                            "attempts":retry_cnt
                        })
                    )
                    break

                except Exception as e:
                    logger.warning(f"{task_id} 전송 실패 - {retry_cnt}회차: {e}")
                    await asyncio.sleep(2)

            else:
                await redis.set(
                    TASK_RESULT_PREFIX + task_id,
                    json.dumps({
                        "status":"failed",
                        "to":email_data["to"],
                        "reason":"전송 3회 실패",
                        "attempts":retry_cnt
                    })
                )
                logger.error(f"{task_id} 전송 최종 실패 (3회 시도 완료)")
            
        except Exception as e:
            logger.error(f"워커 처리 중 예외: {e}")

async def register_pending_status(task_id:str,to_email:str):
    """상태 등록 함수"""
    await redis.set(
        TASK_RESULT_PREFIX + task_id,
        json.dumps({
            "status":"pending",
            "to":to_email
        })
    )
    logger.info(f"{task_id} 상태 등록: pending")

async def get_response_status(task_id:str):
    """응답 조회 함수(API에서 사용)"""
    raw = await redis.get(TASK_RESULT_PREFIX + task_id)
    if raw:
        return json.loads(raw)
    return None