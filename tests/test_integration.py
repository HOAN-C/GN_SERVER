# 통합 테스트

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import check_and_notify, lambda_handler
from history.history_manager import get_new_notices, load_history, save_history
from subscribers.subscribers import get_active_subscribers, load_subscribers

class TestIntegration(unittest.TestCase):
    """통합 테스트"""
    
    def setUp(self):
        """테스트 전 설정"""
        # 테스트용 임시 파일들
        self.test_history_file = "test_history.json"
        self.test_subscribers_file = "test_subscribers.json"
    
    def tearDown(self):
        """테스트 후 정리"""
        # 테스트 파일들 삭제
        for file in [self.test_history_file, self.test_subscribers_file]:
            if os.path.exists(file):
                os.remove(file)
    
    @patch('main.fetch_notice_list')
    @patch('main.fetch_notice_content')
    @patch('main.summarize_notice')
    @patch('main.send_telegram_message')
    @patch('main.send_email')
    @patch('main.send_discord_announcement')
    @patch('main.get_active_subscribers')
    def test_check_and_notify_success(self, mock_subscribers, mock_discord, mock_email, 
                                    mock_telegram, mock_summarize, mock_content, mock_list):
        """전체 워크플로우 성공 테스트"""
        # Mock 설정
        mock_list.return_value = [
            {
                'title': '테스트 공지사항',
                'url': 'https://test.com',
                'date': '2025.01.23',
                'writer': '관리자'
            }
        ]
        
        mock_content.return_value = {
            'title': '테스트 공지사항',
            'content': '테스트 내용',
            'writer': '관리자',
            'date': '2025.01.23'
        }
        
        mock_summarize.return_value = "테스트 요약"
        mock_telegram.return_value = True
        mock_email.return_value = True
        mock_discord.return_value = True
        mock_subscribers.return_value = [
            {'email': 'test@example.com', 'active': True}
        ]
        
        # 테스트 실행
        result = check_and_notify()
        
        # 검증
        self.assertEqual(result['status'], 'success')
        self.assertIn('count', result)
    
    @patch('main.fetch_notice_list')
    def test_check_and_notify_no_new_notices(self, mock_list):
        """새로운 공지사항이 없는 경우 테스트"""
        # Mock 설정
        mock_list.return_value = [
            {
                'title': '기존 공지사항',
                'url': 'https://test.com',
                'date': '2025.01.22',
                'writer': '관리자'
            }
        ]
        
        # 테스트 실행
        result = check_and_notify()
        
        # 검증
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['count'], 0)
    
    @patch('main.fetch_notice_list')
    def test_check_and_notify_crawling_failure(self, mock_list):
        """크롤링 실패 테스트"""
        # Mock 설정
        mock_list.return_value = []
        
        # 테스트 실행
        result = check_and_notify()
        
        # 검증
        self.assertEqual(result['status'], 'error')
    
    def test_lambda_handler_success(self):
        """Lambda 핸들러 성공 테스트"""
        with patch('main.check_and_notify') as mock_check:
            mock_check.return_value = {'status': 'success', 'count': 1}
            
            # 테스트 실행
            result = lambda_handler({}, {})
            
            # 검증
            self.assertEqual(result['statusCode'], 200)
            body = json.loads(result['body'])
            self.assertEqual(body['status'], 'success')
    
    def test_lambda_handler_error(self):
        """Lambda 핸들러 에러 테스트"""
        with patch('main.check_and_notify') as mock_check:
            mock_check.side_effect = Exception("테스트 에러")
            
            # 테스트 실행
            result = lambda_handler({}, {})
            
            # 검증
            self.assertEqual(result['statusCode'], 500)
            body = json.loads(result['body'])
            self.assertIn('error', body)

class TestHistoryManager(unittest.TestCase):
    """히스토리 관리자 테스트"""
    
    def setUp(self):
        """테스트 전 설정"""
        self.test_file = "test_history.json"
    
    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_load_history_empty(self):
        """빈 히스토리 로드 테스트"""
        result = load_history(self.test_file)
        self.assertEqual(result, [])
    
    def test_save_and_load_history(self):
        """히스토리 저장 및 로드 테스트"""
        test_notices = [
            {'title': '테스트1', 'url': 'https://test1.com'},
            {'title': '테스트2', 'url': 'https://test2.com'}
        ]
        
        # 저장
        save_history(test_notices, self.test_file)
        
        # 로드
        result = load_history(self.test_file)
        
        # 검증
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], '테스트1')
    
    def test_get_new_notices_first_run(self):
        """첫 실행 시 모든 공지사항 저장 테스트"""
        test_notices = [
            {'title': '테스트1', 'url': 'https://test1.com'},
            {'title': '테스트2', 'url': 'https://test2.com'}
        ]
        
        result = get_new_notices(test_notices, self.test_file)
        
        # 첫 실행이므로 새로운 공지사항 없음
        self.assertEqual(result, [])
        
        # 히스토리에 저장되었는지 확인
        saved = load_history(self.test_file)
        self.assertEqual(len(saved), 2)

class TestSubscribers(unittest.TestCase):
    """구독자 관리 테스트"""
    
    def setUp(self):
        """테스트 전 설정"""
        self.test_file = "test_subscribers.json"
    
    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_load_subscribers_empty(self):
        """빈 구독자 로드 테스트"""
        result = load_subscribers(self.test_file)
        self.assertEqual(result, [])
    
    def test_get_active_subscribers(self):
        """활성 구독자 필터링 테스트"""
        test_subscribers = [
            {'email': 'active@test.com', 'active': True},
            {'email': 'inactive@test.com', 'active': False},
            {'email': 'no_flag@test.com'}  # active 플래그 없음
        ]
        
        # 테스트 파일에 저장
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump({'subscribers': test_subscribers}, f, ensure_ascii=False, indent=2)
        
        # 활성 구독자 가져오기
        result = get_active_subscribers(self.test_file)
        
        # 검증 (active=True이거나 플래그가 없는 경우)
        self.assertEqual(len(result), 2)
        emails = [sub['email'] for sub in result]
        self.assertIn('active@test.com', emails)
        self.assertIn('no_flag@test.com', emails)

if __name__ == '__main__':
    unittest.main() 