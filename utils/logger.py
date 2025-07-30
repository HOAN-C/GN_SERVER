# 통일된 로깅 시스템

import logging
import sys
from datetime import datetime
from typing import Optional

class GNLogger:
    """GachonNotifier (GN) 프로젝트 전용 로거"""
    
    def __init__(self, name: str, level: int = logging.INFO):
        """
        Args:
            name (str): 로거 이름 (모듈명)
            level (int): 로그 레벨
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 이미 핸들러가 설정되어 있으면 추가하지 않음
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """로그 핸들러 설정"""
        # 콘솔 핸들러
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # 핸들러 추가
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """정보 로그"""
        self.logger.info(message)
    
    def success(self, message: str):
        """성공 로그"""
        self.logger.info(f"✅ {message}")
    
    def warning(self, message: str):
        """경고 로그"""
        self.logger.warning(f"⚠️ {message}")
    
    def error(self, message: str):
        """에러 로그"""
        self.logger.error(f"❌ {message}")
    
    def debug(self, message: str):
        """디버그 로그"""
        self.logger.debug(f"🐛 {message}")
    
    def start(self, message: str):
        """시작 로그"""
        self.logger.info(f"🔄 {message}")
    
    def step(self, step_num: int, total_steps: int, message: str):
        """단계별 로그"""
        self.logger.info(f"📋 [{step_num}/{total_steps}] {message}")
    
    def process(self, current: int, total: int, message: str):
        """진행 상황 로그"""
        self.logger.info(f"📝 [{current}/{total}] {message}")
    
    def send(self, service: str, message: str):
        """알림 전송 로그"""
        self.logger.info(f"🚨 [{service}] {message}")
    
    def result(self, message: str):
        """결과 로그"""
        self.logger.info(f"📊 {message}")


# 모듈별 로거 인스턴스
def get_logger(name: str) -> GNLogger:
    """모듈별 로거를 가져옵니다."""
    return GNLogger(name)


# 기본 로거 (main.py용)
main_logger = get_logger("main")
crawler_logger = get_logger("crawler")
notifier_logger = get_logger("notifier")
ai_logger = get_logger("ai")
history_logger = get_logger("history")
subscriber_logger = get_logger("subscriber") 