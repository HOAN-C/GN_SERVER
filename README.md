# 🎓 GachonNotifier (GN) - 가천대 공지 알리미

가천대학교 공지사항을 자동으로 크롤링하고 AI 요약과 함께 실시간으로 알림을 보내는 스마트 알리미 시스템입니다.

## ✨ 주요 기능

- 🔍 **자동 크롤링**: 가천대학교 공지사항 자동 수집
- 🤖 **AI 요약**: OpenAI GPT를 활용한 공지사항 자동 요약
- 📧 **다중 알림**: 이메일, 텔레그램, 디스코드 알림 지원
- 🌐 **웹 API**: 구독자 관리 및 시스템 제어 API
- 📊 **실시간 모니터링**: 새로운 공지사항 실시간 감지
- 🔄 **스케줄링**: 자동 실행 및 주기적 점검

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐
│   스케줄러        │───▶│   main.py       │
│   (1시간마다)     │    │   (메인 시스템)    │
└─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   가천대학교       │◀───│   크롤러          │───▶│   히스토리        │
│   공지사항        │    │   (Playwright)   │    │   관리자         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI 요약기       │◀───│   새로운 공지      │───▶│   알림 시스템     │
│   (OpenAI GPT)  │    │    확인           │   │   (이메일/텔레그램) │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐
│   웹 API 서버     │   (독립적으로 실행)
│   (Flask)       │    - 구독자 관리
│                 │    - 시스템 상태 확인
└─────────────────┘
```

## 🚀 사용 방법

### 1. 단일 실행 (테스트)

```bash
python main.py test
```

### 2. 스케줄러 실행 (자동화)

```bash
python main.py
```

### 3. 웹 API 서버 실행

```bash
python server.py
```

### 4. 단위 테스트 실행

```bash
python main.py unit-tests
```

## 🌐 API 문서

### 서버 상태 확인

```http
GET /api/health
```

**응답:**

```json
{
  "status": "healthy",
  "timestamp": "2025-07-30T22:45:15.123456",
  "service": "GN API Server",
  "environment": "development",
  "cors_mode": "development"
}
```

### 구독자 목록 조회

```http
GET /api/subscribers
```

**응답:**

```json
{
  "success": true,
  "subscribers": [
    {
      "email": "user@example.com",
      "subscribed_at": "2025-07-30T16:17:52.065405",
      "active": true
    }
  ],
  "count": 1,
  "total_count": 1
}
```

### 구독 신청

```http
POST /api/subscribe
Content-Type: application/json

{
  "email": "newuser@example.com"
}
```

**응답:**

```json
{
  "success": true,
  "message": "구독이 완료되었습니다.",
  "subscriber": {
    "email": "newuser@example.com",
    "subscribed_at": "2025-07-30T22:45:15.123456",
    "active": true
  }
}
```

### 구독 해제

```http
POST /api/unsubscribe
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**응답:**

```json
{
  "success": true,
  "message": "구독이 해제되었습니다."
}
```

## 📁 프로젝트 구조

```
gn_server/
├── main.py                 # 메인 실행 파일
├── server.py              # 웹 API 서버
├── config.py              # 설정 파일
├── requirements.txt       # 의존성 목록
├── .env                   # 환경변수 (gitignore)
├── .gitignore            # Git 무시 파일
├── README.md             # 프로젝트 문서
├── AI/                   # AI 요약 모듈
│   └── AI_summarizer.py
├── crawler/              # 크롤링 모듈
│   ├── notice_list_crawler.py
│   └── notice_crawler.py
├── history/              # 히스토리 관리
│   ├── history_manager.py
│   └── history.json
├── notifier/             # 알림 모듈
│   ├── email_notifier.py
│   ├── telegram.py
│   └── discord.py
├── subscribers/          # 구독자 관리
│   ├── subscribers.py
│   └── subscribers.json
├── tests/                # 테스트 코드
│   ├── test_simple.py
│   ├── test_crawler.py
│   ├── test_notifier.py
│   └── test_integration.py
└── utils/                # 유틸리티
    └── logger.py
```

## 🔧 설정 옵션

### 크롤링 설정

- `TARGET_URL`: 크롤링할 공지사항 URL
- 크롤링 주기: `main.py`에서 스케줄러 설정

### 알림 설정

- 이메일: SMTP 서버 설정
- 텔레그램: 봇 토큰 및 채팅 ID
- 디스코드: 봇 토큰

### AI 요약 설정

- OpenAI API 키 필요
- 요약 길이 및 스타일 조정 가능

## 🧪 테스트

### 단위 테스트

```bash
python -m pytest tests/test_simple.py -v
python -m pytest tests/test_crawler.py -v
python -m pytest tests/test_notifier.py -v
```

### 통합 테스트

```bash
python -m pytest tests/test_integration.py -v
```

### 전체 테스트

```bash
python main.py unit-tests
```

## 📊 모니터링

### 로그 확인

시스템은 다음과 같은 로그를 생성합니다:

- `🔄`: 시스템 시작/진행
- `✅`: 성공 메시지
- `⚠️`: 경고 메시지
- `❌`: 에러 메시지
- `📋`: 단계별 진행
- `📝`: 처리 중인 항목
- `🚨`: 알림 전송
- `📊`: 결과 요약

## 🔒 보안

### API 보안

- CORS 설정으로 허용된 도메인만 접근 가능
- 프로덕션 환경에서는 인증 시스템 추가 권장

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/HOAN-C/GN_SERVER/issues)
- **문의**: hoan.c9907@gmail.com

---

**GachonNotifier** - 가천대학교 공지사항을 더 스마트하게! 🎓✨
