import uuid
from fastapi import APIRouter, HTTPException
from server.log.logger import logger
from server.models.email_DTO import EmailRequest
from server.utils.worker_util import email_queue

router = APIRouter(
    prefix="/api/v1/email",
    tags=["UserEmailReceived"]
)

@router.post("/received")
async def email_received(request: EmailRequest):
    """
    이메일 전송 요청 API
    ## Args:
        - request: 이메일 요청(이메일 주소, 제목, 내용, 사용자 이름)
    """
    try:
        # task_id 생성
        task_id = str(uuid.uuid4())

        # 요청 데이터 구성
        email_data = request.model_dump()
        email_data["task_id"] = task_id

        # 큐에 등록
        await email_queue.put(email_data)
        logger.info(f"{task_id} 이메일 전송 요청 수신 및 큐 등록 완료")

        return {"task_id":task_id,"status":"queued"}
    except Exception as e:
        logger.error(f"[요청 처리 실패] {e}")
        raise HTTPException(
            status_code=500,
            detail="요청 처리 중 오류가 발생했습니다. 관리자에게 문의하세요."
        )