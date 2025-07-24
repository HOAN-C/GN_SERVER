# 알림 모듈 테스트

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notifier.telegram import send_telegram_message
from notifier.email_notifier import send_email
from notifier.discord import send_discord_announcement

class TestTelegramNotifier(unittest.TestCase):
    """텔레그램 알림 테스트"""
    
    @patch('notifier.telegram.requests.post')
    def test_send_telegram_message_success(self, mock_post):
        """텔레그램 메시지 전송 성공 테스트"""
        # Mock 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # 테스트 실행
        result = send_telegram_message("테스트 메시지")
        
        # 검증
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('notifier.telegram.requests.post')
    def test_send_telegram_message_failure(self, mock_post):
        """텔레그램 메시지 전송 실패 테스트"""
        # Mock 설정
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        # 테스트 실행
        result = send_telegram_message("테스트 메시지")
        
        # 검증
        self.assertFalse(result)
    
    @patch('notifier.telegram.requests.post')
    def test_send_telegram_message_exception(self, mock_post):
        """텔레그램 메시지 전송 예외 테스트"""
        # Mock 설정 - 예외 발생
        mock_post.side_effect = Exception("네트워크 오류")
        
        # 테스트 실행
        result = send_telegram_message("테스트 메시지")
        
        # 검증
        self.assertFalse(result)

class TestEmailNotifier(unittest.TestCase):
    """이메일 알림 테스트"""
    
    @patch('notifier.email_notifier.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """이메일 전송 성공 테스트"""
        # Mock 설정
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # 테스트 실행
        result = send_email("테스트 제목", "테스트 내용", "test@example.com")
        
        # 검증
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('notifier.email_notifier.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        """이메일 전송 실패 테스트"""
        # Mock 설정 - 예외 발생
        mock_smtp.side_effect = Exception("SMTP 오류")
        
        # 테스트 실행
        result = send_email("테스트 제목", "테스트 내용", "test@example.com")
        
        # 검증
        self.assertFalse(result)

class TestDiscordNotifier(unittest.TestCase):
    """디스코드 알림 테스트"""
    
    @patch('notifier.discord.requests.post')
    def test_send_discord_announcement_success(self, mock_post):
        """디스코드 알림 전송 성공 테스트"""
        # Mock 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # 테스트 실행
        result = send_discord_announcement("테스트 메시지")
        
        # 검증
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('notifier.discord.requests.post')
    def test_send_discord_announcement_failure(self, mock_post):
        """디스코드 알림 전송 실패 테스트"""
        # Mock 설정
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_post.return_value = mock_response
        
        # 테스트 실행
        result = send_discord_announcement("테스트 메시지")
        
        # 검증
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main() 