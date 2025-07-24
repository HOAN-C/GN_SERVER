# GachonNotifier (GN) API 서버
# 구독자 관리

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 모든 도메인에서 접근 허용

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
        'service': 'GN API Server'
    })

@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    """구독자 목록 조회"""
    try:
        subscribers = load_subscribers()
        return jsonify({
            'success': True,
            'subscribers': subscribers,
            'count': len(subscribers)
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
        
        # 중복 확인
        if any(sub['email'] == email for sub in subscribers):
            return jsonify({
                'success': False,
                'error': '이미 등록된 이메일 주소입니다.'
            }), 409
        
        # 새 구독자 추가
        new_subscriber = {
            'email': email,
            'subscribed_at': datetime.now().isoformat(),
            'active': True
        }
        
        subscribers.append(new_subscriber)
        
        if save_subscribers(subscribers):
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
    print("🚀 API 서버 시작")
    print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌐 서버 주소: http://0.0.0.0:5000")
    
    # 개발 모드에서 실행
    app.run(host='0.0.0.0', port=5001, debug=True) 