"""환경변수 로드 및 상수 정의."""

import os
from dotenv import load_dotenv

load_dotenv()

# 텔레그램
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

# 업비트
UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY", "")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY", "")

# 빗썸
BITHUMB_API_KEY = os.getenv("BITHUMB_API_KEY", "")
BITHUMB_SECRET_KEY = os.getenv("BITHUMB_SECRET_KEY", "")

# 바이낸스
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "")

# OKX
OKX_API_KEY = os.getenv("OKX_API_KEY", "")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY", "")

# Bybit
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
BYBIT_SECRET_KEY = os.getenv("BYBIT_SECRET_KEY", "")

# MEXC
MEXC_API_KEY = os.getenv("MEXC_API_KEY", "")
MEXC_SECRET_KEY = os.getenv("MEXC_SECRET_KEY", "")

# Gate
GATE_API_KEY = os.getenv("GATE_API_KEY", "")
GATE_SECRET_KEY = os.getenv("GATE_SECRET_KEY", "")

# 블록스캔
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")

# 알림 임계값
KIMCHI_ALERT_PCT = float(os.getenv("KIMCHI_ALERT_PCT", "1.5"))
BASIS_ALERT_PCT = float(os.getenv("BASIS_ALERT_PCT", "-0.5"))
POLL_INTERVAL_SEC = int(os.getenv("POLL_INTERVAL_SEC", "30"))
ALERT_COOLDOWN_SEC = int(os.getenv("ALERT_COOLDOWN_SEC", "300"))

# 감시 코인 기본 목록
DEFAULT_WATCH_COINS = ["BTC", "ETH", "XRP", "SOL", "DOGE"]
