"""텔레그램 커맨드 핸들러 — 비즈니스 로직은 monitor 모듈에 위임."""

from telegram import Update
from telegram.ext import ContextTypes

from config import DEFAULT_WATCH_COINS, KIMCHI_ALERT_PCT, BASIS_ALERT_PCT
from exchanges import upbit, bithumb
from monitor.spread import check_spread
from bot.alerts import format_spread_report, format_status_summary

# 런타임 감시 목록
_watch_coins: set[str] = set(DEFAULT_WATCH_COINS)


def get_watch_coins() -> list[str]:
    return sorted(_watch_coins)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/status — 업비트/빗썸 입출금 현황 전체 요약."""
    coins = get_watch_coins()

    upbit_raw = await upbit.fetch_withdrawal_status()
    upbit_status = upbit.parse_wallet_status(upbit_raw, coins)

    bithumb_raw = await bithumb.fetch_asset_status()
    bithumb_status = bithumb.parse_asset_status(bithumb_raw, coins)

    msg = format_status_summary(upbit_status, bithumb_status)
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_spread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/spread — 실시간 김치 프리미엄 + 역현선 현황."""
    coins = get_watch_coins()
    messages = []
    for coin in coins:
        result = await check_spread(coin)
        messages.append(format_spread_report(result))
    await update.message.reply_text("\n\n".join(messages), parse_mode="Markdown")


async def cmd_watch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/watch [코인] — 특정 코인 집중 감시 등록."""
    if not context.args:
        await update.message.reply_text(
            f"현재 감시: {', '.join(get_watch_coins())}\n"
            "사용법: /watch BTC"
        )
        return
    coin = context.args[0].upper()
    _watch_coins.add(coin)
    await update.message.reply_text(f"\u2705 {coin} 감시 등록 완료")


async def cmd_unwatch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/unwatch [코인] — 감시 해제."""
    if not context.args:
        await update.message.reply_text("사용법: /unwatch BTC")
        return
    coin = context.args[0].upper()
    _watch_coins.discard(coin)
    await update.message.reply_text(f"\u274c {coin} 감시 해제 완료")


async def cmd_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/threshold — 알림 임계값 조회."""
    await update.message.reply_text(
        f"\U0001f4ca *알림 임계값*\n"
        f"김치 프리미엄: ±{KIMCHI_ALERT_PCT}%\n"
        f"역현선 basis: {BASIS_ALERT_PCT}%",
        parse_mode="Markdown",
    )
