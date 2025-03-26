from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError

# RequestValidationError handler
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "입력값이 올바르지 않습니다. 이메일 주소와 필수 항목을 다시 확인해주세요.",
            "errors": exc.errors()
            }
    )