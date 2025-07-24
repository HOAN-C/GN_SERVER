# AI 요약 기능

from openai import OpenAI
from config import OPENAI_API_KEY
from crawler.notice_crawler import fetch_notice_content
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger("ai")

# OpenAI 클라이언트 설정
client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_notice(title, content, max_length=250):
    """
    공지사항을 AI로 요약합니다.
    
    Args:
        title (str): 공지사항 제목
        content (str): 공지사항 내용
        max_length (int): 요약 최대 길이
    
    Returns:
        str: 요약된 내용
    """
    logger.start("AI 요약 생성 중...")
    try:
        prompt = f"""
다음 공지사항을 간단하고 명확하게 요약해주세요:

제목: {title}
내용: {content}

요구사항:
- 핵심 내용만 추출
- {max_length}자 이내로 요약
- 학생들이 알아야 할 중요한 정보 위주로
- 마감일, 신청기간, 문의처 등 중요 정보 포함
- 간결하고 읽기 쉽게 작성
"""

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 대학교 공지사항을 간결하게 요약하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_length,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip()
        logger.success(f"AI 요약 완료: {len(summary)}자")
        return summary
        
    except Exception as e:
        logger.error(f"AI 요약 오류: {e}")
        return f"요약 실패: {title}"

if __name__ == "__main__":
    # 테스트용 코드
    test_notices = [
        {
            "title": "2025-2학기 코드쉐어 교과목 수강신청 안내",
            "url": "https://www.gachon.ac.kr/kor/3104/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGa29yJTJGNDc1JTJGMTExNjAwJTJGYXJ0Y2xWaWV3LmRvJTNGcGFnZSUzRDElMjZzcmNoQ29sdW1uJTNEJTI2c3JjaFdyZCUzRCUyNmJic0NsU2VxJTNEJTI2YmJzT3BlbldyZFNlcSUzRCUyNnJnc0JnbmRlU3RyJTNEJTI2cmdzRW5kZGVTdHIlM0QlMjZpc1ZpZXdNaW5lJTNEZmFsc2UlMjZwYXNzd29yZCUzRCUyNg%3D%3D",
            "date": "2025.07.21",
            "writer": "학사지원팀"
        }
    ]
    
    print("🧪 AI 요약 기능 테스트")
    
    # 테스트용 공지사항 내용 가져오기
    notice_info = fetch_notice_content(test_notices[0]['url'])
    
    if notice_info:
        # 요약용 텍스트 구성
        test_content = f"""
제목: {notice_info.get('title', '제목 없음')}
작성자: {notice_info.get('writer', '작성자 없음')}
등록일: {notice_info.get('date', '날짜 없음')}
조회수: {notice_info.get('views', '조회수 없음')}

내용:
{notice_info.get('content', '내용 없음')}

첨부파일: {len(notice_info.get('attachments', []))}개
"""
        summary = summarize_notice(test_notices[0]['title'], test_content.strip())
    else:
        summary = "공지사항 내용을 가져올 수 없습니다."
    
    print(f"\n📝 {test_notices[0]['title']}")
    print(f"📅 {test_notices[0]['date']} - {test_notices[0]['writer']}")
    print(f"🔗 {test_notices[0]['url']}")
    print(f"📋 요약: {summary}")
