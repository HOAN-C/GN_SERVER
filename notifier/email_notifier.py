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
            {message}
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

def send_welcome_email(email):
    """
    구독 완료 환영 이메일 전송
    
    Args:
        email (str): 구독자 이메일 주소
    
    Returns:
        bool: 전송 성공 여부
    """
    try:
        subject = "🎉 무당이 친구가 되어줘서 고마워요!"
        
        message = f"""
<h2 style="color: #2c3e50; margin-bottom: 20px;">🎉 무당이 친구가 되어줘서 고마워요!</h2>

<p style="font-size: 16px; line-height: 1.6; color: #34495e;">
안녕하세요! <strong>{email}</strong>님<br>
무당이와 친구가 되어주셔서 감사해요! 😊
</p>

<p style="font-size: 15px; line-height: 1.6; color: #34495e;">
이제 새로운 공지사항이 올라오면 AI가 요약해서 바로 알려드릴게요!
</p>

<p style="font-size: 14px; color: #7f8c8d; margin-top: 20px;">
💌 구독 해제가 필요하시면 <a href="https://gachonnotifier.site/" style="color: #3498db;">여기</a>를 클릭해주세요.
</p>
"""
        
        return send_email(subject, message, email)
        
    except Exception as e:
        logger.error(f"환영 이메일 전송 실패 ({email}): {e}")
        return False

def test_email():
    """
    이메일 연결 테스트
    """
    test_subject = "가천대 공지 알리미 서비스 테스트"
    test_message = """

<h1>🐞 가천대 공지 알리미 시스템 테스트</h1>

<p>🚧 가천대 공지 알리미 시스템 점검입니다.</p>


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
