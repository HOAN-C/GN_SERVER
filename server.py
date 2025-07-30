# GachonNotifier (GN) API 서버
# 구독자 관리

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from notifier.email_notifier import send_email, send_welcome_email

# 환경변수 로드
load_dotenv()

app = Flask(__name__)

# 환경별 CORS 설정
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')
IS_PRODUCTION = ENVIRONMENT == 'production'

if IS_PRODUCTION:
    # 프로덕션: 특정 도메인만 허용
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
    if not allowed_origins or allowed_origins == ['']:
        # gachonnotifier.site 도메인 설정
        allowed_origins = ['https://gachonnotifier.site', 'https://www.gachonnotifier.site']
    
    CORS(app, 
         origins=allowed_origins,
         methods=['GET', 'POST', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True,
         max_age=3600)  # 1시간 캐시
    
    print(f"🔒 프로덕션 모드: 허용된 도메인 {allowed_origins}")
else:
    # 개발: 모든 도메인 허용 (개발용)
    CORS(app, 
         origins="*",
         methods=['GET', 'POST', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])
    
    print("🔓 개발 모드: 모든 도메인 허용")

# 구독자 파일 경로
SUBSCRIBERS_FILE = "subscribers/subscribers.json"

def load_subscribers():
    try:
        if os.path.exists(SUBSCRIBERS_FILE):
            with open(SUBSCRIBERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('subscribers', [])
        return []
    except Exception as e:
        print(f"구독자 로드 오류: {e}")
        return []

def save_subscribers(subscribers):
    try:
        data = {
            'subscribers': subscribers,
            'last_updated': datetime.now().isoformat()
        }
        with open(SUBSCRIBERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"구독자 저장 오류: {e}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'GN API Server',
        'environment': ENVIRONMENT,
        'cors_mode': 'production' if IS_PRODUCTION else 'development'
    })

@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    """구독자 목록 조회"""
    try:
        all_subscribers = load_subscribers()
        active_subscribers = [sub for sub in all_subscribers if sub.get('active', True)]
        return jsonify({
            'success': True,
            'subscribers': active_subscribers,
            'count': len(active_subscribers),
            'total_count': len(all_subscribers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/subscribe', methods=['POST'])
def add_subscriber():
    """구독자 추가"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({
                'success': False,
                'error': '이메일 주소가 필요합니다.'
            }), 400
        
        # 이메일 형식 검증 (간단한 검증)
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'error': '올바른 이메일 형식이 아닙니다.'
            }), 400
        
        subscribers = load_subscribers()
        
        # 활성 구독자 중복 확인
        if any(sub['email'] == email and sub.get('active', True) for sub in subscribers):
            return jsonify({
                'success': False,
                'error': '이미 등록된 이메일 주소입니다.'
            }), 409
        
        # 비활성 구독자가 있는지 확인하고 재활성화
        existing_subscriber = None
        for sub in subscribers:
            if sub['email'] == email and not sub.get('active', True):
                existing_subscriber = sub
                break
        
        if existing_subscriber:
            # 기존 구독자 재활성화
            existing_subscriber['active'] = True
            existing_subscriber['subscribed_at'] = datetime.now().isoformat()
            if 'unsubscribed_at' in existing_subscriber:
                del existing_subscriber['unsubscribed_at']
            
            if save_subscribers(subscribers):
                # 재활성화 환영 이메일 전송
                send_welcome_email(email)
                return jsonify({
                    'success': True,
                    'message': '구독이 재활성화되었습니다.',
                    'subscriber': existing_subscriber
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '구독자 저장에 실패했습니다.'
                }), 500
        
        # 새 구독자 추가
        new_subscriber = {
            'email': email,
            'subscribed_at': datetime.now().isoformat(),
            'active': True
        }
        
        subscribers.append(new_subscriber)
        
        if save_subscribers(subscribers):
            # 새 구독자 환영 이메일 전송
            send_welcome_email(email)
            return jsonify({
                'success': True,
                'message': '구독이 완료되었습니다.',
                'subscriber': new_subscriber
            })
        else:
            return jsonify({
                'success': False,
                'error': '구독자 저장에 실패했습니다.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/unsubscribe', methods=['POST'])
def remove_subscriber():
    """구독자 제거"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({
                'success': False,
                'error': '이메일 주소가 필요합니다.'
            }), 400
        
        subscribers = load_subscribers()
        
        # 구독자 찾기
        found = False
        for subscriber in subscribers:
            if subscriber['email'] == email:
                if subscriber['active'] == False:
                    return jsonify({
                        'success': False,
                        'error': '이미 구독이 해제된 이메일 주소입니다.'
                    }), 409
                
                subscriber['active'] = False
                subscriber['unsubscribed_at'] = datetime.now().isoformat()
                found = True
                break
        
        if not found:
            return jsonify({
                'success': False,
                'error': '등록되지 않은 이메일 주소입니다.'
            }), 404
        
        if save_subscribers(subscribers):
            return jsonify({
                'success': True,
                'message': '구독이 해제되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'error': '구독자 정보 저장에 실패했습니다.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



if __name__ == '__main__':
    # 환경변수에서 설정 가져오기
    if IS_PRODUCTION:
        port = int(os.getenv('PORT', 5000))  # 프로덕션: 기본 포트 5000
    else:
        port = int(os.getenv('PORT', 5001))  # 개발: 기본 포트 5001
    debug = not IS_PRODUCTION
    
    print("\n🚀 API 서버 시작")
    print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 서버 주소: http://0.0.0.0:{port}")
    print(f"🔧 디버그 모드: {'켜짐' if debug else '꺼짐'}")
    print(f"🌍 환경: {ENVIRONMENT}")
    print(f"🔒 CORS 모드: {'프로덕션' if IS_PRODUCTION else '개발'}")
    
    # 환경에 따라 실행
    app.run(host='0.0.0.0', port=port, debug=debug) 