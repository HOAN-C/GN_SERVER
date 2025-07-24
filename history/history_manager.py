# 새 공지사항 판별 및 기록 관리

import json
import os
from datetime import datetime
import sys

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger("history")

def load_history(history_file="./history/history.json"):
    """
    기록 파일에서 이전 공지사항 목록을 로드.
    
    Returns:
        list: 이전 공지사항 목록 (없으면 빈 리스트)
    """
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('notices', [])
        return []
    except Exception as e:
        logger.error(f"기록 로드 오류: {e}")
        return []

def save_history(notices, history_file="./history/history.json"):
    """
    현재 공지사항 목록을 기록 파일에 저장.
    
    Args:
        notices (list): 저장할 공지사항 목록
        history_file (str): 기록 파일 경로
    """
    try:
        data = {
            'notices': notices,
            'last_updated': datetime.now().isoformat()
        }
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.success(f"기록 저장 완료: {len(notices)}개 공지사항")
    except Exception as e:
        logger.error(f"기록 저장 오류: {e}")

def update_history(new_notices, history_file="./history/history.json"):
    """
    새로운 공지사항을 기록에 추가.
    
    Args:
        new_notices (list): 추가할 새로운 공지사항 목록
        history_file (str): 기록 파일 경로
    """
    current_notices = load_history(history_file)
    updated_notices = new_notices + current_notices
    if len(updated_notices) > 50:
        updated_notices = updated_notices[:50]
    
    save_history(updated_notices, history_file)

def get_new_notices(crawled_notices, history_file="./history/history.json"):
    """
    현재 공지사항과 기록을 비교하여 새로운 공지사항만 반환.
    
    Args:
        crawled_notices (list): 현재 크롤링한 공지사항 목록
        history_file (str): 기록 파일 경로
    
    Returns:
        list: 새로운 공지사항 목록
    """
    previous_notices = load_history(history_file)
    
    if not previous_notices: # 기록이 없으면 모든 공지사항을 저장 후 종료
        logger.info("첫 실행: 모든 공지사항을 저장")
        update_history(crawled_notices, history_file)
        return []
    
    
    new_notices = [] # 새로운 공지사항
    previous_urls = {notice['url'] for notice in previous_notices}
    
    for notice in crawled_notices:
        if notice['url'] not in previous_urls:
            new_notices.append(notice)

    if new_notices:
        update_history(new_notices, history_file)
        logger.success(f"{len(new_notices)}개의 새로운 공지사항 발견!")
    else:
        logger.info("새로운 공지사항이 없습니다.")
    
    logger.result(f"비교 결과: {len(crawled_notices)}개 중 {len(new_notices)}개가 새로운 공지사항")
    
    return new_notices

# 테스트용 코드
if __name__ == "__main__":
    test_notices = [
        {
            "title": "테스트 공지사항 1",
            "url": "https://example.com/1",
            "date": "2025.01.23",
            "writer": "테스트팀"
        },
        {
            "title": "테스트 공지사항 2", 
            "url": "https://example.com/2",
            "date": "2025.01.23",
            "writer": "테스트팀"
        }
    ]
    
    print("    🧪 [history_manager] 기록 매니저 테스트")
    new_notices = get_new_notices(test_notices)
    
    if new_notices:
        for i, notice in enumerate(new_notices, 1):
            print(f"[{i}] {notice['date']} - {notice['title']} - {notice['writer']}")
            print(f"   → {notice['url']}")