import os
import json
from datetime import datetime
import sys

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger("subscriber")

# 구독자 파일 경로
SUBSCRIBERS_FILE = "subscribers/subscribers.json"

def load_subscribers():
    """구독자 목록을 로드합니다."""
    try:
        if os.path.exists(SUBSCRIBERS_FILE):
            with open(SUBSCRIBERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('subscribers', [])
        return []
    except Exception as e:
        logger.error(f"구독자 로드 오류: {e}")
        return []

def get_active_subscribers():
    """활성 구독자 목록을 반환합니다."""
    subscribers = load_subscribers()
    return [sub for sub in subscribers if sub.get('active', True)]




if __name__ == '__main__':
    print(get_active_subscribers())