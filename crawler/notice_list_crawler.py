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
TARGET_CLASS = "div.scroll-table > table.board-table.horizon > tbody > tr.thumb" #전체공지 데이터 위치

def fetch_notice_list(limit=10):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) #크롬 브라우저를 보이지 않게(headless)
        page = browser.new_page() #새로운 웹 페이지
        logger.start("공지사항 리스트 크롤링 시작")
        try:
            page.goto(NOTICE_URL, wait_until="networkidle") #URL 페이지로 이동
            page.wait_for_selector("div.scroll-table > table.board-table.horizon", timeout=15000) #목표 데이터 나올때까지 대기(최대 15초)
            
            # 공지사항 목록을 파싱하면서 각 공지사항의 실제 URL을 얻기
            notice_list = []
            
            # JavaScript로 공지사항 목록의 모든 링크를 가져와서 실제 URL로 변환
            notice_links = page.evaluate("""
                () => {
                    const links = document.querySelectorAll('div.scroll-table table.board-table.horizon tbody tr.thumb td.td-subject a');
                    return Array.from(links).map(link => {
                        const href = link.getAttribute('href');
                        const title = link.textContent.trim();
                        const row = link.closest('tr');
                        const cells = row.querySelectorAll('td');
                        return {
                            href: href,
                            title: title,
                            writer: cells[2] ? cells[2].textContent.trim() : '',
                            date: cells[3] ? cells[3].textContent.trim() : ''
                        };
                    }).slice(0, """ + str(limit) + """);
                }
            """)
            
            # 각 공지사항에 대해 실제 URL 얻기
            for i, notice_link in enumerate(notice_links):
                try:
                    # JavaScript 함수 호출로 실제 URL 얻기
                    artcl_match = re.search(r"jf_viewArtcl\('kor',\s*'(\d+)'\)", notice_link['href'])
                    if artcl_match:
                        artcl_id = artcl_match.group(1)
                        
                        # JavaScript 함수 호출하여 실제 URL 얻기
                        actual_url = page.evaluate(f"jf_viewArtcl('kor', '{artcl_id}')")
                        
                        # 페이지 이동 대기
                        page.wait_for_timeout(1000)
                        
                        # 현재 URL 가져오기
                        current_url = page.url
                        
                        # URL이 변경되었는지 확인
                        if current_url != NOTICE_URL:
                            url = current_url
                        else:
                            # URL이 변경되지 않았다면 기본 URL 사용
                            url = f"https://www.gachon.ac.kr/kor/7986/subview.do?artclId={artcl_id}"
                        
                        # 제목에서 'N' 표시 제거
                        title = notice_link['title'].replace('N', '').strip()
                        
                        notice_list.append({
                            "title": title, 
                            "url": url, 
                            "date": notice_link['date'], 
                            "writer": notice_link['writer']
                        })
                        
                        # 목록 페이지로 돌아가기
                        page.goto(NOTICE_URL, wait_until="networkidle")
                        page.wait_for_selector("div.scroll-table > table.board-table.horizon", timeout=5000)
                        
                except Exception as e:
                    logger.error(f"공지사항 {i+1} URL 생성 오류: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"크롤링 오류: {e}") #문제가 생기면 에러 메시지 출력하고 빈 리스트 돌려주기
            return []
        finally:
            browser.close() #브라우저 창 닫기

        logger.success(f"공지사항 리스트 크롤링 완료: {len(notice_list)}개")
        return notice_list

# 테스트 코드
if __name__ == "__main__":
    notices = fetch_notice_list()
    if notices:
        for i, notice in enumerate(notices, 1):
            print(f"[notice_list_crawler] [{i}] {notice['date']} - {notice['title']} - {notice['writer']}")
            print(f"[notice_list_crawler]    → {notice['url']}")
    else:
        print("[notice_list_crawler] crawling failed")