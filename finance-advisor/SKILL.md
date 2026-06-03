---
name: finance-advisor
description: >
  综合性个人财务分析助手。当用户请求财务分析、投资建议、行情查询、定投管理、资产配置、仓位调整或每日财务建议时触发。融合实时行情（TickDB）、政治事件分析、投资历史学习，提供每日财务建议及定投持仓调整方案。
---

# Finance Advisor Skill

## Features

综合性个人财务分析助手，融合实盘行情、政治事件分析、投资历史学习，提供每日财务建议及定投持仓调整方案。

**Trigger**: 用户请求财务分析、投资建议、行情查询、定投管理、资产配置、仓位调整、财务建议

---

## Architecture

```
finance-advisor/
├── SKILL.md
├── scripts/
│   └── portfolio_manager.py
└── references/
    ├── data_schema.md
    └── event_analysis.md
```

---

## Workflow

### Step 1: Load Financial Profile

Run `portfolio_manager.py summary` to load profile from `memory/finance-profile.json`. If missing, ask user to provide:

**Required fields**:
- Monthly income (after tax)
- Monthly fixed expenses (housing, loan, insurance, living)
- Assets (cash, stocks, funds, bonds, pension, real estate)
- Liabilities (mortgage, car loan, credit card, student loan)
- Risk preference (conservative/balanced/aggressive)
- Investment goal (retirement, house purchase, wealth freedom, education)
- Current holdings (symbol, cost, shares)

**Storage**: `memory/finance-profile.json`

## Market Data Sources

### Primary: TickDB (tickdb-market-data skill)
- Coverage: 外汇、贵金属、指数、美股、港股、A股、加密货币
- Auto-trial key per query, no persistence
- Docs: https://docs.tickdb.ai

### Market Data Sources (Fallback Chain)

| Priority | Source | Coverage | Free Tier | Key Required |
|----------|--------|----------|-----------|-------------|
| 🥇 Primary | **TickDB** | 外汇、贵金属、指数、美股、港股、A股、加密货币 | Trial key (auto, per-query) | No |
| 🥈 Backup 1 | **Finnhub** | 美股、港股、A股、外汇、加密货币 | 60 calls/min | Yes |
| 🥉 Backup 2 | **Twelve Data** | 美股、港股、A股、外汇、加密货币、ETF | 800 calls/day | Yes |
| 🌀 Fallback | **Yahoo Finance (yfinance)** | 美股、港股、加密货币、ETF | Unlimited | No |

**Fallback rules**:
- TickDB error 1001/3001/3002/3006 → Finnhub
- Finnhub rate limit or error → Twelve Data
- All else fails → yfinance (Python `yfinance` library)

### Data Source Details

#### TickDB (Primary)
- Docs: https://docs.tickdb.ai
- Auto-trial key: `GET https://tickdb.ai/api/public/claw-keys`
- No persistence, fetched per query

#### Finnhub (Backup 1)
- Sign up: https://finnhub.io (free API key)
- Key storage: `memory/finnhub-key.json`
- Symbol format: `AAPL.US`, `700.HK`, `BTCUSDT`

#### Twelve Data (Backup 2)
- Sign up: https://twelvedata.com (free API key)
- Key storage: `memory/twelvedata-key.json`
- Symbol format: `AAPL`, `700.HK`, `BTC/USD`, `XAU/USD`
- Supports A-share: `000001.SZ`, `600519.SH`

#### Yahoo Finance / yfinance (Final Fallback)
- No API key needed, Python library
- Install: `pip install yfinance`
- Symbol format: `AAPL`, `700.HK`, `BTC-USD`, `GC=F` (gold)

### Step 2: Real-time Market Data

Use `tickdb-market-data` skill to fetch real-time quotes for user holdings:
- Stocks/ETFs: price, 24h change, volume
- Crypto: support/resistance, 24h volatility
- Forex/Precious metals: XAUUSD (gold), USDJPY

**Fallback flow**:
1. Try TickDB → if error, try next
2. Try Finnhub (if key available in `memory/finnhub-key.json`)
3. Try Twelve Data (if key available in `memory/twelvedata-key.json`)
4. Use yfinance as last resort

### Finnhub API Quick Reference

| Intent | Endpoint |
|--------|----------|
| Real-time quote | `/v1/quote?symbol={SYMBOL}` |
| Candlestick (K线) | `/v1/stock/candle?symbol={SYMBOL}&resolution=D&count=30` |
| Company info | `/v1/stock/profile2?symbol={SYMBOL}` |
| Market status | `/v1/market-status?exchange=US` |

**Symbol format**: AAPL.US, 700.HK, BTCUSDT (crypto), USDCNH (forex)

**Example**: `curl "https://finnhub.io/api/v1/quote?symbol=700.HK&token=$FINNHUB_KEY"`

### Twelve Data API Quick Reference

| Intent | Endpoint |
|--------|----------|
| Real-time quote | `/v1/quote?symbol={SYMBOL}` |
| Price | `/v1/price?symbol={SYMBOL}` |
| Candlestick (K线) | `/v1/time_series?symbol={SYMBOL}&interval=1day&count=30` |
| Currency pair | `/v1/price?symbol=ETH/USD` |

**Symbol format**: `AAPL`, `700.HK`, `BTC/USD`, `XAU/USD`, `000001.SZ`, `600519.SH`

**Example**: `curl "https://api.twelvedata.com/v1/price?symbol=700.HK&apikey=$TWELVEDATA_KEY"`

### Yahoo Finance / yfinance (Final Fallback)

```python
import yfinance as yf

# 美股
aapl = yf.Ticker("AAPL")
print(aapl.info['regularMarketPrice'])

# 港股
hk_700 = yf.Ticker("0700.HK")

# 黄金
gold = yf.Ticker("GC=F")

# 加密货币
btc = yf.Ticker("BTC-USD")

# K线
data = yf.download("AAPL", period="1mo", interval="1d")
```

### Step 3: Investment History Learning

Read `memory/trades.json` and analyze:
- Holdings cost vs current price → unrealized P&L
- Trade history → win rate, avg holding period
- DCA records → accumulated shares, cost averaging

### Step 4: Political Event Analysis

Use web_search to fetch major macro/political events from last 3 days:
- Geopolitics: US-China relations, Middle East, Russia-Ukraine
- Monetary policy: Fed rate decisions, CPI, NFP
- Fiscal policy: US debt ceiling, tariff policy
- Industry policy: China tech regulation, US chip act

### Step 5: Daily Financial Advice Generation

Combine Steps 1-4 and generate daily advice.

### Step 6: Periodic Portfolio Rebalancing (DCA)

**Triggers** (any one):
- Monthly rebalancing day (1st/15th)
- Any single holding deviates from target > 5%
- Market剧烈波动 (SPX daily change > 2%)

---

## Commands

```bash
# Initialize financial profile
python3 scripts/portfolio_manager.py init --salary 45000 --cash 200000

# Add trade record
python3 scripts/portfolio_manager.py add-trade --symbol VOO.US --side buy --quantity 10 --price 420.50 --date 2025-01-15

# View holdings summary
python3 scripts/portfolio_manager.py summary

# Generate rebalancing advice
python3 scripts/portfolio_manager.py rebalance
```

---

## Dependencies

- Python 3.8+
- `requests` library
- `tickdb-market-data` skill (real-time market data)

---

## Limitations

1. **Rate limit**: Free TickDB trial key has frequency limits; register for premium key for high-frequency trading
2. **Not a Financial Advisor**: This skill provides informational advice only; users bear investment risks themselves
3. **Data integrity**: Historical backtest data requires manual import by user