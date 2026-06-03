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

### Step 2: Real-time Market Data

Use `tickdb-market-data` skill to fetch real-time quotes for user holdings:
- Stocks/ETFs: price, 24h change, volume
- Crypto: support/resistance, 24h volatility
- Forex/Precious metals: XAUUSD (gold), USDJPY

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