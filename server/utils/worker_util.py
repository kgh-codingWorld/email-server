import asyncio
from asyncio import Queue
from server.log.logger import logger
from server.utils.email_util import preprocess_email, send_email_async

# 비동기 큐
email_queue = Queue()
response_queue = Queue()

# 응답 저장 공간(임시 캐시)
response_dict = {}

# 이메일 전송 워커
async def email_worker():
    """이메일 전송 워커 함수"""
    while True:
        # 비동기 큐에서 정보 가져옴
        email_data = await email_queue.get()
        task_id = email_data["task_id"]
        retry_cnt = 0

        try:
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
                    result_payload = {

                        "status": "success",
                        "to": email_data["to"],
                        "attempts": retry_cnt
                    }
                    logger.debug(f"응답 큐에 넣기 전 payload: ({task_id}, {result_payload})")
                    await response_queue.put((task_id, result_payload))
                    break

                except Exception as e:
                    logger.warning(f"{task_id} 전송 실패 - {retry_cnt}회차: {e}")
                    await asyncio.sleep(2)

            else:
                result_payload = {
                    "status": "Failed",
                    "to": email_data["to"],
                    "reason": "전송 3회 실패",
                    "attempts": retry_cnt
                }
                logger.debug(f"응답 큐에 넣기 전 payload: ({task_id}, {result_payload})")
                await response_queue.put((task_id, result_payload))
                logger.error(f"{task_id} 전송 최종 실패 (3회 시도 완료)")


        except Exception as e:
            result_payload = {
                "status": "error",
                "to": email_data.get("to", None),
                "reason": str(e)
            }
            logger.debug(f"응답 큐에 넣기 전 payload: ({task_id}, {result_payload})")
            await response_queue.put((task_id, result_payload))
            logger.error(f"[{task_id}] 처리 중 예외 발생: {e}")

        finally:
            email_queue.task_done()

# 응답 워커
async def response_worker():
    """이메일 전송에 대한 응답 워커 함수"""
    while True:
        result_data = await response_queue.get()
        logger.debug(f"큐에서 꺼낸 응답: {result_data}")
        try:
            task_id, result = result_data
            response_dict[task_id] = result
            logger.info(f"응답 큐 처리 완료: task_id={task_id}, 결과 저장")
        except Exception as e:
            logger.error(f"응답 언팩 실패: {e}, 원본: {result_data}")
        finally:
            response_queue.task_done()

# pending
def register_pending_status(task_id:str,to_email:str):
    """pending 상태 등록"""
    response_dict[task_id] = {
        "status":"pending",
        "to":to_email
    }
    logger.info(f"{task_id} 상태 등록: pending")