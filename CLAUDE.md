# CLAUDE.md — 김치 프리미엄 아비트라지 트래커 텔레그램 봇

> **목적**: 주문은 사람이 직접. 봇은 **감시 → 알림**만 담당.

---

## ⛔ 절대 규칙

- **API 키/시크릿 절대 하드코딩 금지** — `.env` + `python-dotenv` 전용
- **거래소 주문 API 절대 호출 금지** — Read-only 조회만 허용
- **무한 루프 반드시 `asyncio.sleep` 포함** — CPU 100% 방지
- **텔레그램 알림 중복 방지** — 동일 이벤트 재알림 금지 (쿨다운 적용)

---

## 🗂 폴더 구조

```
tracker-bot/
├── main.py                  # 진입점: 텔레그램 봇 + 스케줄러 실행
├── config.py                # 환경변수 로드, 상수 정의
├── .env                     # 비밀키 (gitignore)
├── .env.example
│
├── exchanges/
│   ├── upbit.py             # 업비트 API (시세: 공개, 입출금 상태: JWT 인증)
│   ├── bithumb.py           # 빗썸 공개 API (시세, 입출금 상태)
│   └── foreign.py           # 바이낸스/OKX/Bybit/MEXC/Gate 선물 시세 (ccxt, 조회 전용)
│
├── monitor/
│   ├── withdrawal.py        # 입출금 상태 폴링 — 핵심 트리거
│   ├── spread.py            # 김치 프리미엄 / 역현선(basis) 계산
│   └── blockscanner.py      # 온체인 입출금 흐름 감지 (선행 지표)
│
├── bot/
│   ├── handlers.py          # 텔레그램 커맨드 핸들러
│   └── alerts.py            # 알림 메시지 포맷터
│
└── tests/
    ├── test_spread.py
    └── test_withdrawal.py
```

---

## 🛠 기술 스택

| 레이어 | 선택 |
|---|---|
| 런타임 | Python 3.11+ |
| 텔레그램 | `python-telegram-bot` v21 (async) |
| 거래소 조회 | `ccxt` (바이낸스/OKX/Bybit/MEXC/Gate 선물), 업비트/빗썸 공개 REST |
| 블록스캔 | Etherscan / BSCScan API |
| 비동기 | `asyncio` + `aiohttp` |
| 스케줄링 | `APScheduler` |
| 로깅 | `loguru` |
| 테스트 | `pytest` + `pytest-asyncio` |

---

## ⚙️ 빌드 / 실행

```bash
pip install -r requirements.txt

python main.py          # 실행
pytest tests/ -v        # 테스트
```

---

## 📐 도메인 컨텍스트

### 핵심 용어

| 용어 | 의미 |
|---|---|
| 업 | 업비트 (국내 현물) |
| 빗 | 빗썸 (국내 현물) |
| 외국 선 | 바이낸스/OKX/Bybit/MEXC/Gate 선물 |
| 역현선 | 선물 < 현물 — basis 음수 상태 |
| 김치 프리미엄 | 국내 가격 > 해외 현물 가격 차이 (%) |
| 입출금 막힘 | 거래소 입금/출금 일시 정지 |

### 핵심 전략 시나리오

```
블록체인 네트워크 지연/혼잡 발생 (특정 체인)
        ↓
한국 거래소(업비트/빗썸) 입출금 정지
        ↓
코인 이동 불가 → 한국 거래소 내 공급 고립
        ↓
한국 거래소 가격 급등 (펌핑)
        ↓
김치 프리미엄 급격히 확대 (국내 > 해외)
        ↓
해외 선물 역현선(backwardation) 발생
        ↓
★ 역현선 플레이 진입 기회 ★
        ↓
(사람이 직접 판단 후 수동 주문)
```

> 봇의 역할: 위 흐름의 **각 단계를 실시간 감시**하고,
> 기회 조건이 맞을 때 **텔레그램으로 즉시 알림**을 보내는 것.

### 감시 흐름 (기술)

```
[블록스캔] 체인 네트워크 상태/대량 전송 감시 (선행 지표)
        ↓
[업비트/빗썸 API] 입출금 상태 30초 폴링
        ↓
  입출금 정지 감지? → 텔레그램 즉시 알림 ⚠️
        ↓
[시세 조회] 국내 현물 vs 해외 현물/선물 가격 비교
        ↓
  김치 프리미엄 임계값 초과? → 텔레그램 기회 알림 📈
  역현선(basis < 0) 임계값 초과? → 텔레그램 기회 알림 📉
```

### 알림 트리거 조건

1. 업비트 OR 빗썸 특정 코인 **입출금 상태 변경** (정상↔정지) — 가장 중요한 선행 신호
2. 김치 프리미엄 > `KIMCHI_ALERT_PCT` (기본 1.5%) — 갭 확대 감지
3. 역현선 감지 — 선물 basis < `BASIS_ALERT_PCT` (기본 -0.5%) — 진입 기회
4. 블록스캔 대량 온체인 유입/유출 or 네트워크 지연 감지 — 선행 지표

---

## 📣 텔레그램 커맨드

```
/status          — 업비트/빗썸 입출금 현황 전체 요약
/spread          — 실시간 김치 프리미엄 + 역현선 현황
/watch [코인]    — 특정 코인 집중 감시 등록
/unwatch [코인]  — 감시 해제
/threshold       — 알림 임계값 조회/변경
```

---

## 🔑 환경변수 (.env.example)

```env
TELEGRAM_TOKEN=
ADMIN_CHAT_ID=

# 거래소 (조회 전용 — 주문 권한 없는 키 사용 권장)
UPBIT_ACCESS_KEY=
UPBIT_SECRET_KEY=
BITHUMB_API_KEY=
BITHUMB_SECRET_KEY=
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
OKX_API_KEY=
OKX_SECRET_KEY=
BYBIT_API_KEY=
BYBIT_SECRET_KEY=
MEXC_API_KEY=
MEXC_SECRET_KEY=
GATE_API_KEY=
GATE_SECRET_KEY=

# 블록스캔
ETHERSCAN_API_KEY=
BSCSCAN_API_KEY=

# 알림 임계값
KIMCHI_ALERT_PCT=1.5
BASIS_ALERT_PCT=-0.5
POLL_INTERVAL_SEC=30
ALERT_COOLDOWN_SEC=300
```

---

## ✍️ 코딩 컨벤션

```python
# 함수: snake_case, 동사 시작
async def fetch_withdrawal_status(exchange: str, coin: str) -> bool: ...

# 클래스: PascalCase
class SpreadMonitor: ...

# 상수: UPPER_SNAKE_CASE
KIMCHI_ALERT_PCT = 1.5
```

```python
# 비동기: 블로킹 호출 금지
async def poll():
    while True:
        await check_all()
        await asyncio.sleep(POLL_INTERVAL_SEC)  # 필수
```

```python
# 에러: 재시도 3회 후 텔레그램 알림
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def safe_fetch(): ...
```

```
# 커밋
feat: 역현선 알림 임계값 설정 기능 추가
fix: 업비트 입출금 상태 파싱 오류 수정
```

---

## 🚫 하지 말 것

- 거래소 **주문/취소 API 호출** 절대 금지
- `time.sleep()` → `asyncio.sleep()` 사용
- `requests` → `aiohttp` 사용
- 같은 이벤트 중복 알림 — `ALERT_COOLDOWN_SEC` 준수
- 텔레그램 핸들러에 비즈니스 로직 혼재 금지
