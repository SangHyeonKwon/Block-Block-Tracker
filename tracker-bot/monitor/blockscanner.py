"""온체인 입출금 흐름 감지 — Etherscan / BSCScan API."""

import aiohttp
from loguru import logger

from config import ETHERSCAN_API_KEY, BSCSCAN_API_KEY

SCAN_APIS = {
    "etherscan": {
        "base_url": "https://api.etherscan.io/api",
        "api_key": ETHERSCAN_API_KEY,
    },
    "bscscan": {
        "base_url": "https://api.bscscan.com/api",
        "api_key": BSCSCAN_API_KEY,
    },
}

# 알려진 거래소 핫월렛 주소 (예시 — 실제 운영 시 확장 필요)
KNOWN_EXCHANGE_WALLETS: dict[str, list[str]] = {
    "upbit": [],
    "bithumb": [],
    "binance": [],
}


async def fetch_recent_large_transfers(
    scanner: str,
    contract_address: str,
    min_value_usd: float = 100_000,
) -> list[dict]:
    """특정 토큰의 최근 대량 전송 내역 조회."""
    cfg = SCAN_APIS.get(scanner)
    if not cfg or not cfg["api_key"]:
        return []

    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": contract_address,
        "page": 1,
        "offset": 50,
        "sort": "desc",
        "apikey": cfg["api_key"],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(cfg["base_url"], params=params) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                if data.get("status") != "1":
                    return []
                return data.get("result", [])
    except Exception as e:
        logger.error(f"{scanner} 조회 에러: {e}")
        return []


def classify_transfer(tx: dict) -> str | None:
    """전송 방향 분류: 'exchange_inflow', 'exchange_outflow', None."""
    to_addr = tx.get("to", "").lower()
    from_addr = tx.get("from", "").lower()

    all_wallets = set()
    for addrs in KNOWN_EXCHANGE_WALLETS.values():
        all_wallets.update(a.lower() for a in addrs)

    if to_addr in all_wallets:
        return "exchange_inflow"
    if from_addr in all_wallets:
        return "exchange_outflow"
    return None
