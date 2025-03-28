import re
from aiosmtplib import send
from email.message import EmailMessage
from server.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FORCE_FAIL

def build_email_message(to:str,subject:str,body:str,username:str)->EmailMessage:
    """
    이메일 메시지 생성 함수
    ## Args:
        - to: 이메일 주소
        - subject: 제목
        - body: 본문
        - username: 사용자 이름
    """
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    return message

async def send_email_async(to:str,subject:str,body:str,username:str):
    """
    비동기로 이메일 전송 함수
    ## Args:
        - to: 이메일 주소
        - subject: 제목
        - body: 본문
        - username: 사용자 이름
    """
    message = build_email_message(to,subject,body,username)
    await send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USER,
        password=SMTP_PASS,
    )

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