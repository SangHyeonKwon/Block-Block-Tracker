<p align="center">
  <h1 align="center">Block Block Tracker</h1>
  <p align="center">
    <strong>Kimchi Premium Arbitrage Intelligence for Telegram</strong>
    <br />
    Real-time monitoring of Korean exchange deposit/withdrawal locks, kimchi premium spreads, and futures backwardation — so you never miss a window.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Bot" />
  <img src="https://img.shields.io/badge/mode-read--only-green?style=for-the-badge" alt="Read-only" />
  <img src="https://img.shields.io/badge/async-asyncio%20%2B%20aiohttp-764ABC?style=for-the-badge" alt="Async" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <i>The bot watches. You decide. You trade.</i>
</p>

---

## How It Works

The bot exploits a well-known market microstructure pattern in Korean crypto markets:

```
   Blockchain network congestion detected (on-chain scanner)
                          |
                          v
    Korean exchanges suspend deposits/withdrawals
                          |
                          v
     Coin supply becomes isolated on Korean exchanges
                          |
                          v
     Korean price pumps --> Kimchi premium widens
                          |
                          v
     Foreign futures enter backwardation (futures < spot)
                          |
                          v
  +-----------------------------------------------+
  |     BOT SENDS TELEGRAM ALERT                  |
  |     "Opportunity detected -- ACT NOW"         |
  +-----------------------------------------------+
                          |
                          v
          You review, decide, and trade manually
```

> **Block Block Tracker monitors every stage of this pipeline** and alerts you the moment conditions align -- typically seconds after exchange wallet locks change.

---

## Features

| | Feature | Description |
|---|---|---|
| **Deposit/Withdrawal Monitor** | Polls Upbit and Bithumb wallet status every 30 seconds. Instantly alerts when any coin's deposit or withdrawal status flips between active and suspended. |
| **Kimchi Premium Tracker** | Calculates the real-time price gap (%) between Korean spot markets (KRW) and foreign spot prices (USD), alerting when it exceeds your configured threshold. |
| **Futures Basis Scanner** | Monitors perpetual and dated futures on Binance, OKX, Bybit, MEXC, and Gate. Detects backwardation (negative basis) -- the key entry signal. |
| **On-Chain Intelligence** | Watches Etherscan and BSCScan for large transfers and network congestion -- a leading indicator that exchange wallets may lock soon. |
| **Smart Alerting** | Cooldown-based deduplication ensures you get notified once per event, not spammed. Configurable thresholds for every trigger. |
| **Telegram-Native** | Full control from your phone. Check status, adjust watchlists, and change alert thresholds without touching the server. |

---

## Architecture

```
tracker-bot/
|
+-- main.py                     # Entry point: Telegram bot + APScheduler
+-- config.py                   # Env var loader, constants
+-- .env / .env.example         # Secrets (gitignored)
|
+-- exchanges/
|   +-- upbit.py                # Upbit REST API (prices, wallet status via JWT)
|   +-- bithumb.py              # Bithumb public API (prices, wallet status)
|   +-- foreign.py              # Binance/OKX/Bybit/MEXC/Gate futures via ccxt
|
+-- monitor/
|   +-- withdrawal.py           # Deposit/withdrawal status poller (core trigger)
|   +-- spread.py               # Kimchi premium + basis calculator
|   +-- blockscanner.py         # On-chain flow detection (leading indicator)
|
+-- bot/
|   +-- handlers.py             # Telegram command handlers
|   +-- alerts.py               # Alert message formatter
|
+-- tests/
    +-- test_spread.py
    +-- test_withdrawal.py
```

**Data flow:**

```
Etherscan/BSCScan ---+
                     |     +------------------+     +------------------+
Upbit API ---------->+---->|    Monitors      |---->|  Telegram Alerts |----> You
                     |     | (withdrawal,     |     |  (formatted,     |
Bithumb API --------+     |  spread, chain)  |     |   deduplicated)  |
                     |     +------------------+     +------------------+
Binance/OKX/etc. ---+
```

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/your-org/block-block-tracker.git
cd block-block-tracker/tracker-bot

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys (see [Environment Variables](#environment-variables) below).

### 3. Run

```bash
python main.py
```

### 4. Test

```bash
pytest tests/ -v
```

---

## Telegram Commands

| Command | Description |
|---|---|
| `/status` | Full summary of deposit/withdrawal status across Upbit and Bithumb |
| `/spread` | Live kimchi premium (%) and futures basis across all monitored pairs |
| `/watch [COIN]` | Add a coin to focused monitoring (e.g., `/watch ETH`) |
| `/unwatch [COIN]` | Remove a coin from the watchlist |
| `/threshold` | View or adjust alert threshold values |

---

## Environment Variables

Create a `.env` file in the `tracker-bot/` directory. All secrets are loaded via `python-dotenv` -- **nothing is ever hardcoded**.

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_TOKEN` | Yes | Telegram Bot API token from @BotFather |
| `ADMIN_CHAT_ID` | Yes | Your Telegram chat ID for receiving alerts |
| `UPBIT_ACCESS_KEY` | Yes | Upbit API key (read-only recommended) |
| `UPBIT_SECRET_KEY` | Yes | Upbit API secret |
| `BITHUMB_API_KEY` | Yes | Bithumb API key (read-only recommended) |
| `BITHUMB_SECRET_KEY` | Yes | Bithumb API secret |
| `BINANCE_API_KEY` | No | Binance API key (read-only) |
| `BINANCE_SECRET_KEY` | No | Binance API secret |
| `OKX_API_KEY` | No | OKX API key (read-only) |
| `OKX_SECRET_KEY` | No | OKX API secret |
| `BYBIT_API_KEY` | No | Bybit API key (read-only) |
| `BYBIT_SECRET_KEY` | No | Bybit API secret |
| `MEXC_API_KEY` | No | MEXC API key (read-only) |
| `MEXC_SECRET_KEY` | No | MEXC API secret |
| `GATE_API_KEY` | No | Gate.io API key (read-only) |
| `GATE_SECRET_KEY` | No | Gate.io API secret |
| `ETHERSCAN_API_KEY` | No | Etherscan API key for on-chain scanning |
| `BSCSCAN_API_KEY` | No | BSCScan API key for BSC chain scanning |
| `KIMCHI_ALERT_PCT` | No | Kimchi premium alert threshold, default `1.5` (%) |
| `BASIS_ALERT_PCT` | No | Futures basis alert threshold, default `-0.5` (%) |
| `POLL_INTERVAL_SEC` | No | Polling interval, default `30` (seconds) |
| `ALERT_COOLDOWN_SEC` | No | Dedup cooldown per event, default `300` (seconds) |

> **Use read-only API keys with no withdrawal or trading permissions.** This bot never places orders, but defense in depth is good practice.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.11+ |
| Async | `asyncio` + `aiohttp` |
| Telegram | `python-telegram-bot` v21 (async-native) |
| Exchange Data | `ccxt` (Binance, OKX, Bybit, MEXC, Gate -- futures, read-only) |
| Korean Exchanges | Upbit REST + JWT, Bithumb public REST |
| On-Chain | Etherscan / BSCScan APIs |
| Scheduling | `APScheduler` 3.x |
| Retry Logic | `tenacity` (exponential backoff, 3 attempts) |
| Logging | `loguru` |
| Testing | `pytest` + `pytest-asyncio` |

---

## Alert Triggers

The bot fires a Telegram notification when any of these conditions are met:

| # | Trigger | Why It Matters |
|---|---|---|
| 1 | **Deposit/withdrawal status change** on Upbit or Bithumb | The most important leading signal -- supply isolation begins here |
| 2 | **Kimchi premium** exceeds `KIMCHI_ALERT_PCT` | Confirms the gap is widening and the market is reacting |
| 3 | **Futures basis** drops below `BASIS_ALERT_PCT` | Backwardation detected -- potential entry opportunity |
| 4 | **Large on-chain transfers** or network congestion | Early warning before exchanges even announce wallet locks |

---

## Safety and Disclaimer

```
+------------------------------------------------------------------+
|                                                                  |
|   THIS BOT IS STRICTLY READ-ONLY.                               |
|                                                                  |
|   - It will NEVER place, modify, or cancel any exchange order.   |
|   - It will NEVER call any trading or withdrawal API endpoint.   |
|   - It only reads public market data and wallet status.          |
|                                                                  |
|   All trading decisions are made by you, the human operator.     |
|                                                                  |
+------------------------------------------------------------------+
```

- **No financial advice.** This tool provides market data alerts, not trading recommendations.
- **Use at your own risk.** The authors are not responsible for any trading losses.
- **API keys should be read-only** with zero trading or withdrawal permissions.
- Duplicate alerts are suppressed via configurable cooldown (`ALERT_COOLDOWN_SEC`).

---

<p align="center">
  <sub>Built for traders who watch the kimchi premium. Not for bots that trade it.</sub>
</p>
