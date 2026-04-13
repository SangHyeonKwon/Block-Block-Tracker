"""입출금 상태 폴링 — 상태 변경 감지 시 알림 트리거."""

import time
from loguru import logger

from exchanges import upbit, bithumb
from config import ALERT_COOLDOWN_SEC

# 이전 상태 캐시: {(exchange, coin, direction): bool}
_prev_status: dict[tuple[str, str, str], bool] = {}
# 마지막 알림 시각: {(exchange, coin, direction): float}
_last_alert_time: dict[tuple[str, str, str], float] = {}


def _should_alert(key: tuple[str, str, str]) -> bool:
    """쿨다운 기간 이내 중복 알림 방지."""
    last = _last_alert_time.get(key, 0)
    return (time.time() - last) >= ALERT_COOLDOWN_SEC


def _record_alert(key: tuple[str, str, str]) -> None:
    _last_alert_time[key] = time.time()


async def check_withdrawal_changes(coins: list[str]) -> list[dict]:
    """업비트/빗썸 입출금 상태 변경을 감지하고 변경 목록을 반환."""
    changes = []

    # 업비트
    upbit_raw = await upbit.fetch_withdrawal_status()
    upbit_status = upbit.parse_wallet_status(upbit_raw, coins)
    for coin, status in upbit_status.items():
        for direction in ("deposit", "withdraw"):
            key = ("upbit", coin, direction)
            current = status[direction]
            prev = _prev_status.get(key)
            if prev is not None and prev != current and _should_alert(key):
                changes.append(
                    {
                        "exchange": "업비트",
                        "coin": coin,
                        "direction": "입금" if direction == "deposit" else "출금",
                        "status": "정상" if current else "정지",
                    }
                )
                _record_alert(key)
                logger.info(f"업비트 {coin} {direction}: {prev} → {current}")
            _prev_status[key] = current

    # 빗썸
    bithumb_raw = await bithumb.fetch_asset_status()
    bithumb_status = bithumb.parse_asset_status(bithumb_raw, coins)
    for coin, status in bithumb_status.items():
        for direction in ("deposit", "withdraw"):
            key = ("bithumb", coin, direction)
            current = status[direction]
            prev = _prev_status.get(key)
            if prev is not None and prev != current and _should_alert(key):
                changes.append(
                    {
                        "exchange": "빗썸",
                        "coin": coin,
                        "direction": "입금" if direction == "deposit" else "출금",
                        "status": "정상" if current else "정지",
                    }
                )
                _record_alert(key)
                logger.info(f"빗썸 {coin} {direction}: {prev} → {current}")
            _prev_status[key] = current

    return changes


def get_current_status() -> dict[tuple[str, str, str], bool]:
    """현재 캐시된 입출금 상태 반환 (테스트/조회용)."""
    return dict(_prev_status)


def reset_state() -> None:
    """상태 초기화 (테스트용)."""
    _prev_status.clear()
    _last_alert_time.clear()
