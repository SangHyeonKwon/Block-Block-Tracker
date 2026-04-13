"""업비트 API — 시세 조회 (공개), 입출금 상태 조회 (인증 필요)."""

import uuid

import aiohttp
import jwt
from loguru import logger

from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY

BASE_URL = "https://api.upbit.com/v1"

_session: aiohttp.ClientSession | None = None


async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session


def _build_auth_header() -> dict[str, str]:
    """업비트 JWT 인증 헤더 생성."""
    payload = {
        "access_key": UPBIT_ACCESS_KEY,
        "nonce": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, UPBIT_SECRET_KEY, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


async def fetch_ticker(coin: str) -> dict | None:
    """KRW 마켓 현재가 조회. 예: coin='BTC' → KRW-BTC."""
    market = f"KRW-{coin.upper()}"
    url = f"{BASE_URL}/ticker"
    try:
        session = await _get_session()
        async with session.get(url, params={"markets": market}) as resp:
            if resp.status != 200:
                logger.warning(f"업비트 시세 조회 실패: {resp.status}")
                return None
            data = await resp.json()
            return data[0] if data else None
    except Exception as e:
        logger.error(f"업비트 시세 조회 에러: {e}")
        return None


async def fetch_withdrawal_status() -> list[dict]:
    """전체 코인 입출금 상태 조회 (인증 필요)."""
    if not UPBIT_ACCESS_KEY or not UPBIT_SECRET_KEY:
        logger.warning("업비트 API 키 미설정 — 입출금 상태 조회 불가")
        return []
    url = f"{BASE_URL}/status/wallet"
    headers = _build_auth_header()
    try:
        session = await _get_session()
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                logger.warning(f"업비트 입출금 상태 조회 실패: {resp.status}")
                return []
            return await resp.json()
    except Exception as e:
        logger.error(f"업비트 입출금 상태 에러: {e}")
        return []


def parse_wallet_status(raw: list[dict], coins: list[str]) -> dict[str, dict]:
    """입출금 상태를 {코인: {deposit: bool, withdraw: bool}} 형태로 파싱.

    True = 정상, False = 정지.
    """
    result = {}
    coin_set = {c.upper() for c in coins}
    for item in raw:
        currency = item.get("currency", "").upper()
        if currency not in coin_set:
            continue
        result[currency] = {
            "deposit": item.get("wallet_state") in ("working", "deposit_only"),
            "withdraw": item.get("wallet_state") in ("working", "withdraw_only"),
        }
    return result
