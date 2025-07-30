# 공지사항 크롤링 코드
# 고정 공지사항 제외하고 일반 공지사항만 필터링

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger("crawler")

NOTICE_URL = "https://www.gachon.ac.kr/kor/7986/subview.do" #전체공지
# NOTICE_URL = "https://www.gachon.ac.kr/kor/3104/subview.do" #학사공지
TARGET_CLASS = "div.scroll-table > table.board-table.horizon > tbody > tr.thumb" #전체공지 데이터 위치

def fetch_notice_list(limit=10):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) #크롬 브라우저를 보이지 않게(headless)
        page = browser.new_page() #새로운 웹 페이지
        logger.start("공지사항 리스트 크롤링 시작")
        try:
            page.goto(NOTICE_URL, wait_until="networkidle") #URL 페이지로 이동
            page.wait_for_selector("div.scroll-table > table.board-table.horizon", timeout=15000) #목표 데이터 나올때까지 대기(최대 15초)
            html_content = page.content() #웹페이지의 모든 내용을 복사해오기
            
        except Exception as e:
            logger.error(f"크롤링 오류: {e}") #문제가 생기면 에러 메시지 출력하고 빈 리스트 돌려주기
            return []
        finally:
            browser.close() #브라우저 창 닫기

    if not html_content:
        return []

    try:
        soup = BeautifulSoup(html_content, "html.parser") #BeautifulSoup으로 웹페이지 내용을 분석하기 쉽게 만들기
        notice_list = []

        rows = soup.select(TARGET_CLASS) #공지사항이 있는 행들(tr)을 모두 찾기
        
        # 고정 공지사항 제외하고 일반 공지사항만 필터링
        normal_notices = [row for row in rows if not row.get("class") or "notice" not in row.get("class", [])]

        for i, row in enumerate(normal_notices[:limit]): #각 행에서 공지사항 정보를 하나씩 뽑아내기
            columns = row.find_all("td") #각 행의 칸들(td)을 찾기
            
            if len(columns) >= 4:  # 칸이 4개 이상 있어야 함 (번호, 제목, 작성자, 날짜)
                title_link = columns[1].find("a") #제목 링크 찾기
                if title_link:
                    title = title_link.get_text(strip=True) #제목 텍스트 가져오기
                    
                    # 제목에서 'N' 표시 제거 (새로운 공지사항 표시)
                    title = title.replace('N', '').strip()
                    
                    # href 속성에서 JavaScript 함수 호출 추출
                    href_attr = title_link.get("href", "") #링크의 href 속성 가져오기
                    
                    # href에서 JavaScript 함수 호출 추출
                    # 예: javascript:jf_viewArtcl('kor', '111776') → artcl_id=111776
                    id_match = re.search(r"jf_viewArtcl\('kor',\s*'(\d+)'\)", href_attr)
                    
                    if id_match:
                        artcl_id = id_match.group(1) #글 번호 가져오기
                        url = f"https://www.gachon.ac.kr/bbs/kor/7986/{artcl_id}/artclView.do" #실제 공지사항 링크 만들기
                        date = columns[3].get_text(strip=True) #날짜 가져오기
                        writer = columns[2].get_text(strip=True) #작성자 가져오기
                        notice_list.append({"title": title, "url": url, "date": date, "writer": writer}) #정보를 리스트에 추가하기

        logger.success(f"공지사항 리스트 크롤링 완료: {len(notice_list)}개")
        return notice_list
    except Exception as e:
        logger.error(f"크롤링 오류: {e}")
        return []

# 테스트 코드
if __name__ == "__main__":
    notices = fetch_notice_list()
    if notices:
        for i, notice in enumerate(notices, 1):
            print(f"[notice_list_crawler] [{i}] {notice['date']} - {notice['title']} - {notice['writer']}")
            print(f"[notice_list_crawler]    → {notice['url']}")
    else:
        print("[notice_list_crawler] crawling failed")