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
    ## Args:
        - task_id: 요청 받은 task ID
    """
    # 요청 큐에서 저장한 값(응답 보내려고 저장함)에서 task_id 가져오기
    result = response_dict.get(task_id)
    logger.info(f"task_id: {task_id}")
    logger.info(f"result: {result}")
    # result가 none일 때(response_dict가 none 또는 task_id가 none)
    if result is None:
        return {
            "status":"processing",
            "message":"이메일 전송이 아직 처리 중입니다."
        }
    
    return result