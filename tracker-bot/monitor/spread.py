"""김치 프리미엄 / 역현선(basis) 계산."""

import aiohttp
from loguru import logger

from exchanges import upbit, foreign
from config import KIMCHI_ALERT_PCT, BASIS_ALERT_PCT

# 환율 캐시
_cached_usd_krw: float | None = None


async def fetch_usd_krw() -> float:
    """USD/KRW 환율 조회 (공개 API)."""
    global _cached_usd_krw
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    rate = data["rates"].get("KRW")
                    if rate:
                        _cached_usd_krw = rate
                        return rate
    except Exception as e:
        logger.error(f"환율 조회 에러: {e}")

    if _cached_usd_krw:
        logger.warning("캐시된 환율 사용")
        return _cached_usd_krw
    return 1350.0  # 폴백 기본값


def calc_kimchi_premium(krw_price: float, usd_price: float, usd_krw: float) -> float:
    """김치 프리미엄 (%) 계산.

    양수 = 국내가 더 비쌈, 음수 = 해외가 더 비쌈.
    """
    if usd_price <= 0 or usd_krw <= 0 or krw_price <= 0:
        return 0.0
    foreign_krw = usd_price * usd_krw
    return ((krw_price - foreign_krw) / foreign_krw) * 100


def calc_basis(spot_usd: float, futures_usd: float) -> float:
    """역현선 basis (%) 계산.

    음수 = 선물 < 현물 (역현선 상태).
    """
    if spot_usd <= 0:
        return 0.0
    return ((futures_usd - spot_usd) / spot_usd) * 100


async def check_spread(coin: str) -> dict:
    """특정 코인의 김치 프리미엄 + 역현선 현황 조회."""
    usd_krw = await fetch_usd_krw()

    # 업비트 KRW 가격
    upbit_ticker = await upbit.fetch_ticker(coin)
    krw_price = float(upbit_ticker["trade_price"]) if upbit_ticker else 0.0

    # 해외 선물 가격
    futures_prices = await foreign.fetch_all_futures_prices(coin)

    # 바이낸스 선물가를 기준으로 김치 프리미엄 계산
    binance_price = futures_prices.get("binance")
    kimchi_pct = 0.0
    if binance_price and krw_price:
        kimchi_pct = calc_kimchi_premium(krw_price, binance_price, usd_krw)

    # 각 거래소별 basis 계산 (바이낸스 현물 대비)
    basis_results = {}
    for ex_name, fut_price in futures_prices.items():
        if fut_price and binance_price:
            basis_results[ex_name] = calc_basis(binance_price, fut_price)

    alerts = []
    if abs(kimchi_pct) >= KIMCHI_ALERT_PCT:
        alerts.append(f"김프 {kimchi_pct:+.2f}%")
    for ex_name, basis in basis_results.items():
        if basis <= BASIS_ALERT_PCT:
            alerts.append(f"{ex_name} 역현선 {basis:+.2f}%")

    return {
        "coin": coin,
        "krw_price": krw_price,
        "usd_krw": usd_krw,
        "kimchi_pct": kimchi_pct,
        "futures": futures_prices,
        "basis": basis_results,
        "alerts": alerts,
    }
