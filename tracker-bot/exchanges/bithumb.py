"""빗썸 공개 API — 시세 조회, 입출금 상태 조회."""

import aiohttp
from loguru import logger

BASE_URL = "https://api.bithumb.com/public"


async def fetch_ticker(coin: str) -> dict | None:
    """현재가 조회."""
    url = f"{BASE_URL}/ticker/{coin.upper()}_KRW"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.warning(f"빗썸 시세 조회 실패: {resp.status}")
                    return None
                data = await resp.json()
                if data.get("status") != "0000":
                    logger.warning(f"빗썸 시세 에러: {data.get('message')}")
                    return None
                return data.get("data")
    except Exception as e:
        logger.error(f"빗썸 시세 조회 에러: {e}")
        return None


async def fetch_asset_status() -> dict:
    """전체 코인 입출금 상태 조회."""
    url = f"{BASE_URL}/assetsstatus/ALL"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.warning(f"빗썸 입출금 상태 조회 실패: {resp.status}")
                    return {}
                data = await resp.json()
                if data.get("status") != "0000":
                    return {}
                return data.get("data", {})
    except Exception as e:
        logger.error(f"빗썸 입출금 상태 에러: {e}")
        return {}


def parse_asset_status(raw: dict, coins: list[str]) -> dict[str, dict]:
    """입출금 상태를 {코인: {deposit: bool, withdraw: bool}} 형태로 파싱."""
    result = {}
    coin_set = {c.upper() for c in coins}
    for currency, info in raw.items():
        if currency.upper() not in coin_set:
            continue
        result[currency.upper()] = {
            "deposit": info.get("deposit_status") == 1,
            "withdraw": info.get("withdrawal_status") == 1,
        }
    return result
