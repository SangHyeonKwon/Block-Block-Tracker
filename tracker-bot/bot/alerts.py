"""알림 메시지 포맷터."""


def format_withdrawal_change(change: dict) -> str:
    """입출금 상태 변경 알림 메시지."""
    emoji = "\u2705" if change["status"] == "정상" else "\u26d4"
    return (
        f"{emoji} [{change['exchange']}] {change['coin']} "
        f"{change['direction']} → {change['status']}"
    )


def format_withdrawal_changes(changes: list[dict]) -> str:
    """여러 입출금 변경을 하나의 메시지로."""
    if not changes:
        return ""
    lines = ["\U0001f6a8 *입출금 상태 변경 감지*\n"]
    for c in changes:
        lines.append(format_withdrawal_change(c))
    return "\n".join(lines)


def format_spread_report(result: dict) -> str:
    """스프레드 현황 보고 메시지."""
    coin = result["coin"]
    krw = result["krw_price"]
    kimchi = result["kimchi_pct"]
    usd_krw = result["usd_krw"]

    lines = [
        f"\U0001f4ca *{coin} 스프레드 현황*",
        f"업비트: {krw:,.0f} KRW",
        f"환율: {usd_krw:,.1f} KRW/USD",
        f"김치 프리미엄: {kimchi:+.2f}%",
        "",
        "*역현선 (basis)*",
    ]

    for ex_name, basis in result.get("basis", {}).items():
        indicator = "\U0001f534" if basis <= -0.5 else "\U0001f7e2"
        lines.append(f"  {indicator} {ex_name}: {basis:+.2f}%")

    if result.get("alerts"):
        lines.append("")
        lines.append("\u26a0\ufe0f *알림*: " + " | ".join(result["alerts"]))

    return "\n".join(lines)


def format_status_summary(
    upbit_status: dict[str, dict],
    bithumb_status: dict[str, dict],
) -> str:
    """전체 입출금 현황 요약."""
    lines = ["\U0001f4cb *입출금 현황 요약*\n"]

    lines.append("*업비트*")
    for coin, s in sorted(upbit_status.items()):
        dep = "\u2705" if s["deposit"] else "\u26d4"
        wit = "\u2705" if s["withdraw"] else "\u26d4"
        lines.append(f"  {coin}: 입금{dep} 출금{wit}")

    lines.append("\n*빗썸*")
    for coin, s in sorted(bithumb_status.items()):
        dep = "\u2705" if s["deposit"] else "\u26d4"
        wit = "\u2705" if s["withdraw"] else "\u26d4"
        lines.append(f"  {coin}: 입금{dep} 출금{wit}")

    return "\n".join(lines)
