"""진입점: 텔레그램 봇 + 스케줄러 실행."""

import asyncio
from loguru import logger
from telegram.ext import ApplicationBuilder, CommandHandler

from config import TELEGRAM_TOKEN, ADMIN_CHAT_ID, POLL_INTERVAL_SEC
from bot.handlers import (
    cmd_status,
    cmd_spread,
    cmd_watch,
    cmd_unwatch,
    cmd_threshold,
    get_watch_coins,
)
from bot.alerts import format_withdrawal_changes
from monitor.withdrawal import check_withdrawal_changes


async def poll_loop(app) -> None:
    """입출금 상태 변경 폴링 루프."""
    logger.info(f"폴링 시작 (간격: {POLL_INTERVAL_SEC}초)")
    while True:
        try:
            coins = get_watch_coins()
            changes = await check_withdrawal_changes(coins)
            if changes:
                msg = format_withdrawal_changes(changes)
                await app.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=msg,
                    parse_mode="Markdown",
                )
        except Exception as e:
            logger.error(f"폴링 에러: {e}")
        await asyncio.sleep(POLL_INTERVAL_SEC)


def main() -> None:
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # 커맨드 핸들러 등록
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("spread", cmd_spread))
    app.add_handler(CommandHandler("watch", cmd_watch))
    app.add_handler(CommandHandler("unwatch", cmd_unwatch))
    app.add_handler(CommandHandler("threshold", cmd_threshold))

    logger.info("봇 시작")

    # 폴링 루프를 post_init에서 시작
    async def post_init(app) -> None:
        asyncio.create_task(poll_loop(app))

    app.post_init = post_init
    app.run_polling()


if __name__ == "__main__":
    main()
