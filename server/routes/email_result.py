from fastapi import APIRouter, Query, HTTPException
from server.utils.worker_util import get_response_status
from server.log.logger import logger

router = APIRouter(
    prefix="/api/v1/email",
    tags=["EmailStatusResponse"]
)

@router.get("/result")
async def get_email_result(task_id:str=Query(...)):
    """
    이메일 요청 처리 상태 조회 API
    ## Args:
        - task_id: 요청 받은 task ID
    """
    try:
        result = await get_response_status(task_id)
        if not result:
            return {
                "status":"processing",
                "message": "이메일 전송이 아직 처리 중입니다."
            }
        logger.info(f"task_id: {task_id}")
        logger.info(f"result: {result}")
        return result
    except Exception as e:
        logger.error(f"결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="결과 조회 중 오류가 발생했습니다.")