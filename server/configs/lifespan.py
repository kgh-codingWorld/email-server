import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from server.utils.worker_util import email_worker
from server.log.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 앱의 lifespan 관리 함수"""
    logger.info("Email Worker Started")
    # 워커 실행
    for _ in range(2): # 동시에 2개까지 처리(큐 기반)
        asyncio.create_task(email_worker())
    yield
    logger.info("Email Worker Shutdown")