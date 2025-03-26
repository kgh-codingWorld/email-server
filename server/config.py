import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

SMTP_HOST=os.getenv("SMTP_HOST")
SMTP_PORT=int(os.getenv("SMTP_PORT"))
SMTP_USER=os.getenv("SMTP_USER")
SMTP_PASS=os.getenv("SMTP_PASS")

EMAIL_FORCE_FAIL = False