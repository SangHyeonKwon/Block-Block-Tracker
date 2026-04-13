"""입출금 상태 변경 감지 테스트."""

from exchanges.upbit import parse_wallet_status
from exchanges.bithumb import parse_asset_status


def test_upbit_parse_wallet_status():
    raw = [
        {
            "currency": "BTC",
            "wallet_state": "working",
            "block_state": "normal",
        },
        {
            "currency": "ETH",
            "wallet_state": "paused",
            "block_state": "normal",
        },
        {
            "currency": "XRP",
            "wallet_state": "deposit_only",
            "block_state": "normal",
        },
    ]
    result = parse_wallet_status(raw, ["BTC", "ETH", "XRP"])

    assert result["BTC"]["deposit"] is True
    assert result["BTC"]["withdraw"] is True
    assert result["ETH"]["deposit"] is False
    assert result["ETH"]["withdraw"] is False
    assert result["XRP"]["deposit"] is True
    assert result["XRP"]["withdraw"] is False


def test_upbit_parse_filters_coins():
    raw = [
        {"currency": "BTC", "wallet_state": "working"},
        {"currency": "DOGE", "wallet_state": "working"},
    ]
    result = parse_wallet_status(raw, ["BTC"])
    assert "BTC" in result
    assert "DOGE" not in result


def test_bithumb_parse_asset_status():
    raw = {
        "BTC": {"deposit_status": 1, "withdrawal_status": 1},
        "ETH": {"deposit_status": 0, "withdrawal_status": 1},
    }
    result = parse_asset_status(raw, ["BTC", "ETH"])

    assert result["BTC"]["deposit"] is True
    assert result["BTC"]["withdraw"] is True
    assert result["ETH"]["deposit"] is False
    assert result["ETH"]["withdraw"] is True
