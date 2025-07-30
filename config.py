import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 공지사항 URL
# TARGET_URL = "https://www.gachon.ac.kr/kor/3104/subview.do" #학사공지
TARGET_URL = "https://www.gachon.ac.kr/kor/7986/subview.do" #전체 공지

# OpenAI API 키
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 텔레그램 설정
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 이메일 설정
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# 디스코드 봇 설정
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")