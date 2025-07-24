# 이메일 알림 기능

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_RECEIVER
from utils.logger import get_logger

logger = get_logger("notifier")

def send_email(subject, message, recipient_email):
    """
    이메일로 알림을 전송합니다.
    
    Args:
        subject (str): 이메일 제목
        message (str): 이메일 내용
        recipient_email (str): 수신자 이메일
    
    Returns:
        bool: 전송 성공 여부
    """
    # 수신자 이메일 설정
    to_email = recipient_email if recipient_email else EMAIL_RECEIVER
    
    logger.send("email", f"이메일 전송 시작: {to_email}")
    try:
        # 이메일 메시지 구성
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # HTML 형식으로 메시지 작성
        html_message = f"""
        <html>
        <body>
        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 10px;">
            {message.replace('\n', '<br>')}
        </div>
        <hr>
        <p style="color: #666; font-size: 12px;">
            이 메시지는 가천대 공지 알리미 시스템에서 자동으로 전송되었습니다.<br>
            구독 해제를 원하시면 웹사이트에서 해제해주세요.
        </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_message, 'html'))
        
        # SMTP 서버 연결 및 전송
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        
        logger.success(f"이메일 전송 성공: {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"이메일 전송 오류 ({to_email}): {e}")
        return False

def test_email():
    """
    이메일 연결 테스트
    """
    test_subject = "가천대 공지 알리미 서비스 테스트"
    test_message = """
🐞 가천대 공지 알리미 시스템 테스트

🚧 가천대 공지 알리미 시스템 점검입니다.

"""
    
    logger.start("이메일 테스트 시작")
    success = send_email(test_subject, test_message, EMAIL_RECEIVER)
    
    if success:
        logger.success("이메일 테스트 성공!")
    else:
        logger.error("이메일 테스트 실패!")
    
    return success

if __name__ == "__main__":
    test_email()
