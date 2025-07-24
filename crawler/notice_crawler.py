# 공지사항 내용 크롤링

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger("crawler")

def fetch_notice_content(url):
    """
    URL에서 내용을 크롤링.
    
    Args:
        url (str): 공지사항 URL
    
    Returns:
        dict: 공지사항 정보 (제목, 내용, 날짜, 작성자 등)
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle")
            # 페이지 로딩 대기
            page.wait_for_timeout(3000)
            html_content = page.content()
            
        except Exception as e:
            logger.error(f"공지사항 크롤링 오류: {e}")
            return None
        finally:
            browser.close()

    if not html_content:
        return None

    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 공지사항 정보 추출
        notice_info = {}
        
        # 제목 추출 (h2.view-title)
        title_element = soup.select_one("h2.view-title")
        if title_element:
            notice_info['title'] = title_element.get_text(strip=True)
        
        # 작성자 추출
        writer_element = soup.select_one("dl.writer dd")
        if writer_element:
            notice_info['writer'] = writer_element.get_text(strip=True)
        
        # 등록일 추출
        write_element = soup.select_one("dl.write dd")
        if write_element:
            notice_info['date'] = write_element.get_text(strip=True)
        
        # 수정일 추출
        modify_element = soup.select_one("dl.modify dd")
        if modify_element:
            notice_info['modified_date'] = modify_element.get_text(strip=True)
        
        # 조회수 추출
        count_element = soup.select_one("dl.count dd")
        if count_element:
            notice_info['views'] = count_element.get_text(strip=True)
        
        # 내용 추출 (view-con div)
        content_element = soup.select_one("div.view-con")
        if content_element:
            # HTML 태그 제거하고 텍스트만 추출
            content_text = content_element.get_text(strip=True)
            # 여러 줄 공백 정리
            content_text = re.sub(r'\n\s*\n', '\n', content_text)
            content_text = re.sub(r' +', ' ', content_text)
            notice_info['content'] = content_text.strip()
        
        # 첨부파일 추출
        attachments = []
        attachment_elements = soup.select("div.view-file a[href*='download']")
        for attachment in attachment_elements:
            attachments.append({
                'name': attachment.get_text(strip=True),
                'url': attachment.get('href', '')
            })
        notice_info['attachments'] = attachments
        return notice_info
        
    except Exception as e:
        logger.error(f"공지사항 파싱 오류: {e}")
        return None





# 테스트용 코드
if __name__ == "__main__":
    test_url = "https://www.gachon.ac.kr/kor/3104/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGa29yJTJGNDc1JTJGMTExNjAwJTJGYXJ0Y2xWaWV3LmRvJTNGcGFnZSUzRDElMjZzcmNoQ29sdW1uJTNEJTI2c3JjaFdyZCUzRCUyNmJic0NsU2VxJTNEJTI2YmJzT3BlbldyZFNlcSUzRCUyNnJnc0JnbmRlU3RyJTNEJTI2cmdzRW5kZGVTdHIlM0QlMjZpc1ZpZXdNaW5lJTNEZmFsc2UlMjZwYXNzd29yZCUzRCUyNg%3D%3D"
    
    notice_data = fetch_notice_content(test_url)
    
    if notice_data:
        print("📋 공지사항 정보:")
        print(f"제목: {notice_data.get('title', '제목 없음')}")
        print(f"작성자: {notice_data.get('writer', '작성자 없음')}")
        print(f"등록일: {notice_data.get('date', '날짜 없음')}")
        print(f"조회수: {notice_data.get('views', '조회수 없음')}")
        print(f"내용 길이: {len(notice_data.get('content', ''))}자")
        print(f"첨부파일: {len(notice_data.get('attachments', []))}개")
    else:
        print("❌ 크롤링 실패")
