"""해외 거래소 선물 시세 조회 — ccxt (조회 전용)."""

import ccxt.async_support as ccxt
from loguru import logger

from config import (
    BINANCE_API_KEY,
    BINANCE_SECRET_KEY,
    BYBIT_API_KEY,
    BYBIT_SECRET_KEY,
    GATE_API_KEY,
    GATE_SECRET_KEY,
    MEXC_API_KEY,
    MEXC_SECRET_KEY,
    OKX_API_KEY,
    OKX_SECRET_KEY,
)

EXCHANGE_CONFIGS = {
    "binance": {
        "class": ccxt.binance,
        "api_key": BINANCE_API_KEY,
        "secret": BINANCE_SECRET_KEY,
        "options": {"defaultType": "swap"},
    },
    "okx": {
        "class": ccxt.okx,
        "api_key": OKX_API_KEY,
        "secret": OKX_SECRET_KEY,
        "options": {"defaultType": "swap"},
    },
    "bybit": {
        "class": ccxt.bybit,
        "api_key": BYBIT_API_KEY,
        "secret": BYBIT_SECRET_KEY,
        "options": {"defaultType": "swap"},
    },
    "mexc": {
        "class": ccxt.mexc,
        "api_key": MEXC_API_KEY,
        "secret": MEXC_SECRET_KEY,
        "options": {"defaultType": "swap"},
    },
    "gate": {
        "class": ccxt.gate,
        "api_key": GATE_API_KEY,
        "secret": GATE_SECRET_KEY,
        "options": {"defaultType": "swap"},
    },
}


def _create_exchange(name: str) -> ccxt.Exchange | None:
    cfg = EXCHANGE_CONFIGS.get(name)
    if not cfg:
        return None
    return cfg["class"](
        {
            "apiKey": cfg["api_key"],
            "secret": cfg["secret"],
            "options": cfg["options"],
            "enableRateLimit": True,
        }
    )


async def fetch_futures_price(exchange_name: str, coin: str) -> float | None:
    """선물(perpetual swap) 현재가 조회. symbol 예: BTC/USDT:USDT."""
    symbol = f"{coin.upper()}/USDT:USDT"
    exchange = _create_exchange(exchange_name)
    if not exchange:
        return None
    try:
        ticker = await exchange.fetch_ticker(symbol)
        return ticker.get("last")
    except Exception as e:
        logger.error(f"{exchange_name} 선물 시세 조회 에러 ({coin}): {e}")
        return None
    finally:
        await exchange.close()


async def fetch_all_futures_prices(coin: str) -> dict[str, float | None]:
    """모든 해외 거래소의 선물 현재가를 한번에 조회."""
    results = {}
    for name in EXCHANGE_CONFIGS:
        results[name] = await fetch_futures_price(name, coin)
    return results
