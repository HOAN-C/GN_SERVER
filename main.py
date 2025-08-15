import json
import os
import sys
from datetime import datetime

# 모듈 임포트
from crawler.notice_list_crawler import fetch_notice_list
from crawler.notice_crawler import fetch_notice_content
from history.history_manager import get_new_notices
from AI.AI_summarizer import summarize_notice
from notifier.telegram import send_telegram_message
from notifier.email_notifier import send_email
from notifier.discord import send_discord_announcement
from config import TARGET_URL
from subscribers.subscribers import get_active_subscribers
from utils.logger import main_logger

def check_and_notify():
    """
    공지사항 확인 및 알림 전송 메인 함수
    """
    main_logger.start("공지사항 확인 시작")
    
    try:
        main_logger.step(1, 3, "공지사항 리스트 크롤링")
        crawled_notices = fetch_notice_list()
        
        if not crawled_notices:
            main_logger.error("크롤링 실패")
            return {"status": "error", "message": "크롤링 실패"}
        
        main_logger.success(f"{len(crawled_notices)}개 공지사항 크롤링 완료")
        
        main_logger.step(2, 3, "새로운 공지사항 확인")
        new_notices = get_new_notices(crawled_notices)
        
        if not new_notices:
            return {"status": "success", "message": "새로운 공지사항 없음", "count": 0}
        
        # 3. 각 새로운 공지사항에 대해 요약 생성
        main_logger.step(3, 3, "공지사항 요약")

        processed_count = 0
        notification_stack = [] #여러 알림이 있을 시 한번에 알림을 정리해서 전송하기 위한 저장소
        for i, notice in enumerate(new_notices, 1):
            main_logger.process(i, len(new_notices), f"공지사항 요약 시작: {notice['title']}")
            
            try:
                # 3.1 공지사항 내용 크롤링 및 AI 요약
                notice_info = fetch_notice_content(notice['url'])
                
                if notice_info:
                    # 요약용 텍스트 구성
                    notice_content = f"""
제목: {notice_info.get('title', '제목 없음')}
작성자: {notice_info.get('writer', '작성자 없음')}
등록일: {notice_info.get('date', '날짜 없음')}
조회수: {notice_info.get('views', '조회수 없음')}
내용:
{notice_info.get('content', '내용 없음')}

첨부파일: {len(notice_info.get('attachments', []))}개
"""
                    # AI 요약
                    ai_summary = summarize_notice(notice['title'], notice_content.strip())
                else:
                    ai_summary = "공지사항 내용을 가져올 수 없습니다."
                
                # 3.2 알림 메시지 구성
                summarized_notice = f"""
<p style="margin-bottom: 10px;">{ai_summary}</p>

<p>🔗 링크: <a href="{notice['url']}" style="color: #3498db; text-decoration: none;">바로가기</a></p>
"""
                # 구조체 형태로 저장
                notification_stack.append({
                    'title': notice['title'],
                    'message': summarized_notice
                })
                main_logger.success(f"공지사항 요약 완료: {notice['title']}")
                processed_count += 1
                
            except Exception as e:
                main_logger.error(f"공지사항 처리 실패: {e}")
                continue
        


        # 3.3 알림 전송
        main_logger.send("main", "알림 전송")
        
        # 이메일 활성 유저
        active_subscribers = get_active_subscribers()

        if (len(active_subscribers)==0):
            main_logger.info("📭 활성 구독자가 없습니다.")
            return {"status": "success", "message": "활성 구독자가 없습니다.", "count": 0}

        main_logger.info(f"📧 {len(active_subscribers)}명의 구독자에게 이메일 전송")
        success_count = 0

        # 이메일 내용 구분
        title = ''
        message = ''
        if (len(notification_stack)==1):
            title = notification_stack[0]['title']
            message = notification_stack[0]['message']
        else:
            title = f"📢 {len(notification_stack)}개의 새로운 공지사항이 있어요!"
            message = f"""
{''.join([f'''
<div style="margin-bottom: 30px; border: 1px solid #ddd; border-radius: 8px; padding: 15px; background-color: #f8f9fa;">
    <h3 style="margin: 0 0 15px 0; color: #2c3e50; font-size: 16px; border-bottom: 2px solid #3498db; padding-bottom: 8px;">
        📌{item['title']}
    </h3>
    <div style="color: #34495e; line-height: 1.6;">
        {item['message']}
    </div>
</div>
''' for item in notification_stack])}
"""

        for subscriber in active_subscribers:
            try:
                send_email(title, message, subscriber['email'])
                success_count += 1
            except Exception as e:
                main_logger.error(f"이메일 전송 실패 ({subscriber['email']}): {e}")
        
        main_logger.success(f"이메일 알림 전송 완료: {success_count}/{len(active_subscribers)}명")
        
        main_logger.result(f"새로운 공지사항 요약 및 알림 전송 완료 ({processed_count}개)")
        return {
            "status": "success", 
            "message": f"{processed_count}개 공지사항 처리 완료", 
            "count": processed_count
        }
        
    except Exception as e:
        main_logger.error(f"시스템 오류: {e}")
        return {"status": "error", "message": str(e)}

def main():
    """
    GachonNotifier (GN) 메인 실행 함수
    """
    main_logger.start("GN 시스템 시작")
    main_logger.info(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        result = check_and_notify()
        main_logger.success(f"GN 시스템 완료: {result}")
        return result
    except Exception as e:
        main_logger.error(f"GN 시스템 오류: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # 명령행 인수 처리
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # 테스트 모드: 한 번만 실행
            main_logger.start("GN 시스템 테스트 실행")
            result = check_and_notify()
            main_logger.result(f"테스트 결과: {result}")
        elif sys.argv[1] == "unit-tests":
            # 단위 테스트 실행
            import unittest
            import os
            import sys
            
            print("🧪 GN 단위 테스트 실행")
            print("=" * 50)
            
            # 테스트 디렉토리 추가
            test_dir = os.path.join(os.path.dirname(__file__), 'tests')
            sys.path.insert(0, test_dir)
            
            # 테스트 로더 생성
            loader = unittest.TestLoader()
            suite = unittest.TestSuite()
            
            # 테스트 파일들 추가
            test_files = ['test_simple', 'test_crawler', 'test_notifier', 'test_integration']
            
            for test_file in test_files:
                try:
                    test_module = loader.loadTestsFromName(test_file)
                    suite.addTest(test_module)
                    print(f"✅ {test_file} 테스트 로드 완료")
                except Exception as e:
                    print(f"⚠️ {test_file} 테스트 로드 실패: {e}")
            
            # 테스트 실행
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            # 결과 출력
            print("=" * 50)
            print(f"📊 테스트 결과: {result.testsRun}개 실행, {len(result.failures)}개 실패, {len(result.errors)}개 오류")
            
            if result.failures or result.errors:
                sys.exit(1)
            else:
                print("✅ 모든 테스트 성공!")
                sys.exit(0)
        elif sys.argv[1] == "scheduler":
            # 스케줄러 모드 (EC2 cron용)
            import logging
            from pathlib import Path
            
            # 로깅 설정
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('/var/log/gn_scheduler.log'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            
            logger = logging.getLogger(__name__)
            logger.info("=" * 50)
            logger.info("GN 스케줄러 시작")
            logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                result = check_and_notify()
                logger.info(f"스케줄러 완료: {result}")
                
                if result.get('status') == 'success':
                    sys.exit(0)
                else:
                    sys.exit(1)
            except Exception as e:
                logger.error(f"스케줄러 오류: {e}")
                sys.exit(1)
        elif sys.argv[1] == "help":
            print("""
GachonNotifier (GN) - 가천대 공지사항 자동 알림 시스템

사용법:
    python main.py                    # 일반 실행
    python main.py test              # 통합 테스트 (실제 크롤링 및 알림)
    python main.py unit-tests        # 단위 테스트 실행
    python main.py scheduler         # 스케줄러 모드 (EC2 cron용)
    python main.py help              # 도움말 표시

환경 설정:
    - config.py에서 설정 확인
    - 환경변수 설정 필요 (텔레그램, 디스코드, 이메일 토큰 등)

EC2 Cron 설정 예시:
    # 매시간 실행
    0 * * * * cd /home/ubuntu/alg && /home/ubuntu/alg/venv/bin/python main.py scheduler
    
    # 매 30분마다 실행
    */30 * * * * cd /home/ubuntu/alg && /home/ubuntu/alg/venv/bin/python main.py scheduler
            """)
        else:
            print(f"알 수 없는 명령: {sys.argv[1]}")
            print("사용법: python main.py [test|unit-tests|scheduler|help]")
    else:
        # 일반 실행
        main()
