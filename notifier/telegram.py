# 텔레그램 알림 기능

import requests
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from utils.logger import get_logger

logger = get_logger("notifier")

def send_telegram_message(message):
    """
    텔레그램으로 메시지를 전송합니다.
    
    Args:
        message (str): 전송할 메시지
    
    Returns:
        bool: 전송 성공 여부
    """
    logger.send("telegram", "메시지 전송 시작")
    try:
        # 텔레그램 봇 API URL
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # 메시지 데이터
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"  # 마크다운 형식 지원
        }
        
        # API 호출
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.success("텔레그램 메시지 전송 성공")
            return True
        else:
            logger.error(f"텔레그램 전송 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"텔레그램 전송 오류: {e}")
        return False

def test_telegram():
    """
    텔레그램 연결 테스트
    """
    test_message = """
🐞 **가천대 공지 알리미 시스템 테스트**

🚧 가천대 공지 알리미 시스템 점검입니다.
"""
    
    logger.start("텔레그램 연결 테스트 시작")
    success = send_telegram_message(test_message)
    
    if success:
        logger.success("텔레그램 연결 성공!")
    else:
        logger.error("텔레그램 연결 실패!")
    
    return success

if __name__ == "__main__":
    test_telegram()
