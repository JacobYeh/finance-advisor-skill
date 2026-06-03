# 个人财务数据结构参考

## 存储位置

- **主档案**：`~/.openclaw/workspace/memory/finance-profile.json`
- **交易日志**：`~/.openclaw/workspace/memory/trades.json`
- **每日建议**：`~/.openclaw/workspace/memory/daily-reports/YYYY-MM-DD.md`

---

## finance-profile.json Schema

```json
{
  "version": "1.0",
  "created_at": "ISO8601时间戳",
  "updated_at": "ISO8601时间戳",

  "income": {
    "monthly_salary_after_tax": 45000,
    "monthly_bonus_after_tax": 8000,
    "annual_other_income": 0
  },

  "expenses": {
    "monthly_housing": 8000,
    "monthly_loan": 0,
    "monthly_insurance": 1500,
    "monthly_living": 5000,
    "monthly_other": 0
  },

  "assets": {
    "cash_savings": 200000,
    "stocks_etfs": [
      {"symbol": "VOO.US", "shares": 10, "avg_cost": 420.50}
    ],
    "funds": [
      {"name": "易方达蓝筹", "shares": 5000, "avg_cost": 2.10}
    ],
    "bonds": [],
    "crypto": [
      {"symbol": "BTCUSDT", "amount": 0.5, "avg_cost": 45000}
    ],
    "pension": 180000,
    "real_estate": 0
  },

  "liabilities": {
    "mortgage": 0,
    "car_loan": 0,
    "credit_card": 0,
    "student_loan": 0
  },

  "risk_preference": "balanced",
  "investment_goal": "retirement",
  "investment_horizon_years": 10,

  "target_allocation": {
    "stocks_etfs": 60,
    "bonds": 20,
    "gold": 10,
    "cash": 10
  },

  "dca_plan": {
    "enabled": true,
    "monthly_amount_usd": 3000,
    "frequency": "monthly",
    "day_of_month": 1,
    "instruments": ["VOO.US"]
  }
}
```

---

## trades.json Schema

```json
{
  "version": "1.0",
  "trades": [
    {
      "id": "uuid-v4",
      "date": "2025-01-15",
      "symbol": "VOO.US",
      "side": "buy",
      "quantity": 10,
      "price": 420.50,
      "currency": "USD",
      "exchange_rate": 7.25,
      "commission": 1.00,
      "note": "月初定投"
    }
  ]
}
```

---

## 数据初始化建议流程

1. **首次使用**：运行 `portfolio_manager.py init --salary 45000 --cash 200000 --pension 180000 ...`
2. **后续更新**：运行 `portfolio_manager.py update-profile --file /path/to/new_data.json`
3. **交易记录追加**：运行 `portfolio_manager.py add-trade ...`
4. **查看摘要**：运行 `portfolio_manager.py summary`

---

## 资产负债分类指南

### 资产优先级排序

| 优先级 | 资产类别 | 变现能力 | 说明 |
|--------|----------|----------|------|
| 1 | 现金/货币基金 | 实时 | 应急备用金，保留3-6个月支出 |
| 2 | 股票/ETF | T+1 | 核心投资仓位 |
| 3 | 黄金/贵金属 | T+2 | 避险配置 |
| 4 | 基金 | T+1~T+7 | 视基金类型而定 |
| 5 | 债券 | 到期兑付 | 固定收益，稳定现金流 |
| 6 | 养老金 | 退休提取 | 长期锁定，税收优惠 |
| 7 | 房产 | 较长周期 | 自住不计入投资组合 |

### 负债优先级排序

| 优先级 | 负债类型 | 利率 | 说明 |
|--------|----------|------|------|
| 1 | 信用卡 | 15-18% | 最高利率，优先偿还 |
| 2 | 学生贷 | 4-6% | 有税收优惠，次于信用卡 |
| 3 | 车贷 | 5-7% | 实物抵押，利率适中 |
| 4 | 房贷 | 3-5% | 低利率，长期负债，通胀有利 |

---

## 月度财务健康指标

```python
# 计算公式
monthly_net_income = monthly_salary_after_tax + monthly_bonus_after_tax - total_monthly_expenses
savings_rate = monthly_net_income / monthly_salary_after_tax

# 警戒线
savings_rate < 0.10:  "⚠️ 储蓄率过低，需减少非必要支出"
savings_rate > 0.30:  "✅ 储蓄率健康"
debt_to_asset_ratio > 0.50: "⚠️ 负债率过高，需控制新增负债"
emergency_fund_months < 3: "⚠️ 应急储备不足，建议至少保留3个月支出"
```

---

## 定投配置策略

### 核心-卫星配置法

```
目标配置：
├── 核心仓位（70%）：大盘指数ETF，如 VOO.US、SPY.US
├── 卫星仓位（20%）：行业/主题ETF或个股，如 QQQ.US、七大科技股
└── 现金/稳定仓位（10%）：USD稳定币或货币基金
```

### 定投节奏建议

| 资金规模 | 建议频率 | 单次金额（USD） |
|----------|----------|----------------|
| <$10,000 | 每周 | $100-200 |
| $10,000-50,000 | 每两周 | $200-500 |
| >$50,000 | 每月 | $500-2000 |

---

*本文件为参考文档，完整使用说明请查阅 SKILL.md*
---

## API Key 存储位置

| 数据源 | 存储位置 | 备注 |
|--------|----------|------|
| TickDB | 自动获取试用Key | 不持久化，每次实时获取 |
| Finnhub | `memory/finnhub-key.json` | 用户注册后填入 |

**finnhub-key.json 格式**:
```json
{
  "api_key": "your_finnhub_api_key_here",
  "note": "注册于 https://finnhub.io 免费获取"
}
```
