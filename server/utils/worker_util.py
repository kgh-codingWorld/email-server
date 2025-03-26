import asyncio
from server.log.logger import logger
from server.utils.email_util import preprocess_email, send_email

# 비동기 큐
email_queue = asyncio.Queue()

# 응답 저장공간
response_dict = {}

# 워커
async def email_worker():
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

                    await asyncio.to_thread(
                        send_email,
                        email_data["to"],
                        email_data["subject"],
                        email_data["body"],
                        email_data["username"]
                    )

                    logger.info(f"{email_data['to']} 전송 성공")
                    # 응답 보내려고 저장
                    response_dict[task_id] = {
                        "status": "success",
                        "to": email_data["to"],
                        "attempts": retry_cnt
                    }
                    logger.info(f"{task_id} 전송 결과 저장 완료")
                    logger.info(f"결과 확인: {response_dict}")
                    break

                except Exception as e:
                    logger.warning(f"{task_id} 전송 실패 - {retry_cnt}회차: {e}")
                    await asyncio.sleep(2)

            else:
                response_dict[task_id] = {
                    "status": "Failed",
                    "to": email_data["to"],
                    "reason": "전송 3회 실패",
                    "attempts": retry_cnt
                }
                logger.error(f"{task_id} 전송 최종 실패 (3회 시도 완료)")
                logger.info(f"결과 확인: {response_dict}")

        except Exception as e:
            response_dict[task_id] = {
                "status": "error",
                "to": email_data.get("to", None),
                "reason": str(e)
            }
            logger.error(f"[{task_id}] 처리 중 예외 발생: {e}")
            logger.info(f"결과 확인: {response_dict}")

        finally:
            email_queue.task_done()
