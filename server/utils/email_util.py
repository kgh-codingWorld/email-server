import re
import smtplib
from fastapi import HTTPException
from pydantic import EmailStr
from email.mime.text import MIMEText
from server.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FORCE_FAIL
from server import config
from server.log.logger import logger
from fastapi.exceptions import RequestValidationError

def preprocess_email(email:dict)->dict:
    """
    메일 본문, 제목 등 전송 전 전처리 수행
    ## Args:
        - email: 요청 큐에 담긴 email data
    """
    # 제목
    subject = email.get("subject", "").strip().capitalize()
    email["subject"] = subject
    # 본문
    body = email.get("body", "")
    body = re.sub(r"<(script|style).*?>.*?</\1>", "[제거됨]", body, flags=re.DOTALL | re.IGNORECASE)
    # 사용자 이름
    username = email.get("username", "고객님")
    body = body.replace("{username}", username)

    email["body"] = body

    return email


def send_email(to:EmailStr,subject:str,body:str,username:str):
    """
    이메일 전송 함수
    ## Args:
        - to: 수신자 이메일 주소(유효성 검증된 EmailStr)
        - subject: 이메일 제목
        - body: 이메일 본문(텍스트 형식)
    """
    # if to == "forcefail@example.com":
    #     raise Exception("강제 실패 유도(테스트용)")
    
    try:
        # 이메일 메시지 생성(텍스트 기반)
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = to
        msg["Username"] = username

        # SMTP 서버에 연결 및 로그인
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.set_debuglevel(1)
            server.starttls() # 보안 연결(TLS 암호화)
            server.login(SMTP_USER, SMTP_PASS) # 인증: 앱 비밀번호 사용
            server.send_message(msg) # 이메일 전송
            logger.info(f"{to}에게 이메일 보내기")
            
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"smtp 인증실패&&&&&&&&&&&&&&&&&: {e}")
        raise Exception("SMTP 인증 실패") from e
    except smtplib.SMTPConnectError:
        logger.error("SMTP 서버 연결 실패 - 인터넷 상태 확인")
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"잘못된 수신자 이메일 주소: {e.recipients}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP 일반 오류: {e}")
    except RequestValidationError:
        logger.error("형식 오류")
    except HTTPException as e:
        logger.error(f"이메일 전송 실패: {e}")