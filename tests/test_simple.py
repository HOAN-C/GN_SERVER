# 간단한 단위 테스트

import unittest
import sys
import os
import json

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from history.history_manager import load_history, save_history

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

class TestSubscribersLogic(unittest.TestCase):
    """구독자 로직 테스트 (실제 파일 없이)"""
    
    def test_active_subscriber_filtering(self):
        """활성 구독자 필터링 로직 테스트"""
        test_subscribers = [
            {'email': 'active@test.com', 'active': True},
            {'email': 'inactive@test.com', 'active': False},
            {'email': 'no_flag@test.com'}  # active 플래그 없음
        ]
        
        # 활성 구독자 필터링 (실제 함수 로직과 동일)
        active_subscribers = [sub for sub in test_subscribers if sub.get('active', True)]
        
        # 검증 (active=True이거나 플래그가 없는 경우)
        self.assertEqual(len(active_subscribers), 2)
        emails = [sub['email'] for sub in active_subscribers]
        self.assertIn('active@test.com', emails)
        self.assertIn('no_flag@test.com', emails)

class TestConfig(unittest.TestCase):
    """설정 테스트"""
    
    def test_config_import(self):
        """설정 모듈 임포트 테스트"""
        try:
            from config import TARGET_URL, OPENAI_API_KEY
            self.assertIsInstance(TARGET_URL, str)
            # API 키는 환경변수에 따라 None일 수 있음
        except ImportError as e:
            self.fail(f"설정 모듈 임포트 실패: {e}")

class TestFileOperations(unittest.TestCase):
    """파일 작업 테스트"""
    
    def setUp(self):
        """테스트 전 설정"""
        self.test_file = "test_file.json"
    
    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_json_file_operations(self):
        """JSON 파일 읽기/쓰기 테스트"""
        test_data = {
            'subscribers': [
                {'email': 'test@example.com', 'active': True}
            ]
        }
        
        # 쓰기
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # 읽기
        with open(self.test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        # 검증
        self.assertEqual(loaded_data['subscribers'][0]['email'], 'test@example.com')
        self.assertTrue(loaded_data['subscribers'][0]['active'])

if __name__ == '__main__':
    unittest.main() 