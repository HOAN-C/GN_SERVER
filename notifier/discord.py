# 디스코드 봇 알림 기능

import requests
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DISCORD_BOT_TOKEN
from utils.logger import get_logger

logger = get_logger("notifier")

def get_bot_guilds():
    """
    봇이 속한 모든 서버(길드)를 가져옵니다.
    
    Returns:
        list: 서버 ID 목록
    """
    try:
        url = "https://discord.com/api/v10/users/@me/guilds"
        headers = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            guilds = response.json()
            return [guild['id'] for guild in guilds]
        else:
            logger.error(f"서버 목록 가져오기 실패: {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"서버 목록 가져오기 오류: {e}")
        return []

def get_guild_channels(guild_id):
    """
    특정 서버의 모든 채널을 가져옵니다.
    
    Args:
        guild_id (str): 서버 ID
    
    Returns:
        list: 채널 정보 목록 (ID, 이름 포함)
    """
    try:
        url = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
        headers = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            channels = response.json()
            # 텍스트 채널만 필터링하고 이름과 ID 포함
            text_channels = [
                {
                    'id': channel['id'],
                    'name': channel['name'],
                    'type': channel['type']
                }
                for channel in channels 
                if channel['type'] == 0  # 텍스트 채널
            ]
            return text_channels
        else:
            logger.error(f"채널 목록 가져오기 실패: {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"채널 목록 가져오기 오류: {e}")
        return []

def send_discord_message(message, channel_id):
    """
    디스코드 봇으로 메시지를 전송합니다.
    
    Args:
        message (str): 전송할 메시지
        channel_id (str): 채널 ID
    
    Returns:
        bool: 전송 성공 여부
    """
    try:
        # 디스코드 봇 API URL
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        
        # 메시지 데이터
        data = {
            "content": message
        }
        
        # 헤더 설정 (봇 토큰 사용)
        headers = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # API 호출
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.success(f"디스코드 메시지 전송 성공 (채널: {channel_id})")
            return True
        else:
            logger.error(f"디스코드 전송 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"디스코드 전송 오류: {e}")
        return False

def send_discord_announcement(message):
    """
    공지 채널에만 메시지를 전송합니다.
    
    Args:
        message (str): 전송할 메시지
    
    Returns:
        int: 성공한 전송 수
    """
    success_count = 0
    
    # 봇이 속한 모든 서버 가져오기
    guilds = get_bot_guilds()
    logger.info(f"봇이 속한 서버 수: {len(guilds)}")
    
    for guild_id in guilds:
        # 각 서버의 모든 텍스트 채널 가져오기
        channels = get_guild_channels(guild_id)
        logger.info(f"서버 {guild_id}의 텍스트 채널 수: {len(channels)}")
        
        for channel in channels:
            channel_name = channel['name'].lower()  # 소문자로 변환
            
            # 공지 관련 채널만 필터링
            if any(keyword in channel_name for keyword in ['공지', 'announcement', 'notice', '알림', '공지사항']):
                logger.info(f"공지 채널 발견: {channel['name']} (ID: {channel['id']})")
                if send_discord_message(message, channel['id']):
                    success_count += 1
    
    return success_count

def test_discord_bot():
    test_message = """
🐞 **가천대 공지 알리미 시스템 테스트**

🚧 가천대 공지 알리미 시스템 점검입니다.
"""
    
    logger.start("공지 채널 메시지 전송")
    
    success_count = send_discord_announcement(test_message)
    
    if success_count > 0:
        logger.success(f"디스코드 연결 성공! {success_count}개 공지 채널에 메시지 전송")
    else:
        logger.error("디스코드 봇 연결 실패 또는 공지 채널을 찾을 수 없습니다!")
    
    return success_count > 0

if __name__ == "__main__":
    test_discord_bot()
