# 크롤러 모듈 테스트

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.notice_list_crawler import fetch_notice_list
from crawler.notice_crawler import fetch_notice_content

class TestNoticeListCrawler(unittest.TestCase):
    """공지사항 리스트 크롤러 테스트"""
    
    @patch('crawler.notice_list_crawler.sync_playwright')
    def test_fetch_notice_list_success(self, mock_playwright):
        """정상적인 크롤링 테스트"""
        # Mock 설정
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # HTML 콘텐츠 모킹
        mock_html = """
        <div class="scroll-table">
            <table class="board-table horizon1">
                <tbody>
                    <tr>
                        <td>1</td>
                        <td><a onclick="jf_viewArtcl('kor', '475', '110580')">테스트 공지사항</a></td>
                        <td>관리자</td>
                        <td>2025.01.23</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        mock_page.content.return_value = mock_html
        
        # 테스트 실행
        result = fetch_notice_list(limit=1)
        
        # 검증
        self.assertIsInstance(result, list)
        if result:  # 결과가 있는 경우
            self.assertIn('title', result[0])
            self.assertIn('url', result[0])
            self.assertIn('writer', result[0])
            self.assertIn('date', result[0])
    
    @patch('crawler.notice_list_crawler.sync_playwright')
    def test_fetch_notice_list_failure(self, mock_playwright):
        """크롤링 실패 테스트"""
        # Mock 설정 - 예외 발생
        mock_context = MagicMock()
        mock_context.chromium.launch.side_effect = Exception("크롤링 실패")
        mock_playwright.return_value.__enter__.return_value = mock_context
        
        # 테스트 실행
        result = fetch_notice_list()
        
        # 검증
        self.assertEqual(result, [])

class TestNoticeContentCrawler(unittest.TestCase):
    """공지사항 내용 크롤러 테스트"""
    
    @patch('crawler.notice_crawler.sync_playwright')
    def test_fetch_notice_content_success(self, mock_playwright):
        """정상적인 내용 크롤링 테스트"""
        # Mock 설정
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # HTML 콘텐츠 모킹
        mock_html = """
        <h2 class="view-title">테스트 공지사항</h2>
        <dl class="writer"><dd>관리자</dd></dl>
        <dl class="write"><dd>2025.01.23</dd></dl>
        <dl class="count"><dd>100</dd></dl>
        <div class="view-con">테스트 내용입니다.</div>
        """
        mock_page.content.return_value = mock_html
        
        # 테스트 실행
        result = fetch_notice_content("https://test.com")
        
        # 검증
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)
        self.assertIn('writer', result)
        self.assertIn('date', result)
        self.assertIn('content', result)
    
    @patch('crawler.notice_crawler.sync_playwright')
    def test_fetch_notice_content_failure(self, mock_playwright):
        """내용 크롤링 실패 테스트"""
        # Mock 설정 - 예외 발생
        mock_context = MagicMock()
        mock_context.chromium.launch.side_effect = Exception("크롤링 실패")
        mock_playwright.return_value.__enter__.return_value = mock_context
        
        # 테스트 실행
        result = fetch_notice_content("https://test.com")
        
        # 검증
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main() 