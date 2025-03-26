from fastapi import APIRouter, Query
from server.utils.worker_util import response_dict
from server.log.logger import logger

router = APIRouter(
    prefix="/api/v1/email",
    tags=["EmailStatusResponse"]
)

@router.get("/result")
async def get_email_result(task_id:str=Query(...)):
    """
    이메일 요청 처리 상태 조회 API
    """
    result = response_dict.get(task_id)
    logger.info(f"📌task_id: {task_id}")
    logger.info(f"📌result: {result}")
    if result is None:
        return {
            "status":"processing",
            "message":"이메일 전송이 아직 처리 중입니다."
        }
    
    return result