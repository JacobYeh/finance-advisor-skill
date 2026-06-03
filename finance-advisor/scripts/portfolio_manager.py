#!/usr/bin/env python3
"""
Portfolio Manager - 投资组合管理核心脚本
支持财务档案初始化、交易记录管理、持仓摘要、再平衡建议
"""

import json
import os
import sys
import argparse
from datetime import datetime, date
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
PROFILE_FILE = MEMORY_DIR / "finance-profile.json"
TRADES_FILE = MEMORY_DIR / "trades.json"


def ensure_memory_dir():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def load_profile():
    if not PROFILE_FILE.exists():
        return None
    with open(PROFILE_FILE) as f:
        return json.load(f)


def save_profile(profile):
    ensure_memory_dir()
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def load_trades():
    if not TRADES_FILE.exists():
        return {"trades": []}
    with open(TRADES_FILE) as f:
        return json.load(f)


def save_trades(trades):
    ensure_memory_dir()
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=2, ensure_ascii=False)


def cmd_init(args):
    """初始化财务档案"""
    profile = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "income": {
            "monthly_salary_after_tax": args.salary,
            "monthly_bonus_after_tax": args.bonus or 0,
            "annual_other_income": 0
        },
        "expenses": {
            "monthly_housing": args.housing or 0,
            "monthly_loan": args.loan or 0,
            "monthly_insurance": args.insurance or 0,
            "monthly_living": args.living or 3000,
            "monthly_other": 0
        },
        "assets": {
            "cash_savings": args.cash or 0,
            "stocks_etfs": [],
            "funds": [],
            "bonds": [],
            "crypto": [],
            "pension": 0,
            "real_estate": 0
        },
        "liabilities": {
            "mortgage": args.mortgage or 0,
            "car_loan": args.car or 0,
            "credit_card": 0,
            "student_loan": 0
        },
        "risk_preference": args.risk or "balanced",
        "investment_goal": args.goal or "retirement",
        "target_allocation": {
            "stocks_etfs": 60,
            "bonds": 20,
            "gold": 10,
            "cash": 10
        }
    }
    save_profile(profile)
    print(f"✅ 财务档案已创建：{PROFILE_FILE}")


def cmd_add_trade(args):
    """添加交易记录"""
    trades = load_trades()
    trade = {
        "date": args.date,
        "symbol": args.symbol,
        "side": args.side,
        "quantity": float(args.quantity),
        "price": float(args.price),
        "note": args.note or ""
    }
    trades["trades"].append(trade)
    save_trades(trades)
    print(f"✅ 交易记录已添加：{args.side} {args.quantity} {args.symbol} @ ${args.price}")


def cmd_update_profile(args):
    """更新财务档案（从外部JSON文件导入）"""
    source = Path(args.file)
    if not source.exists():
        print(f"❌ 文件不存在：{source}")
        sys.exit(1)
    with open(source) as f:
        new_profile = json.load(f)
    profile = load_profile() or {}
    profile.update(new_profile)
    profile["updated_at"] = datetime.now().isoformat()
    save_profile(profile)
    print(f"✅ 财务档案已更新")


def cmd_summary(args):
    """生成持仓摘要"""
    profile = load_profile()
    trades = load_trades()

    if not profile:
        print("❌ 财务档案不存在，请先运行 init 命令初始化")
        sys.exit(1)

    # 按标的分组计算持仓
    positions = {}
    for t in trades["trades"]:
        sym = t["symbol"]
        if sym not in positions:
            positions[sym] = {"bought": 0, "sold": 0, "avg_cost": 0, "total_cost": 0}
        if t["side"] == "buy":
            positions[sym]["bought"] += t["quantity"]
            positions[sym]["total_cost"] += t["quantity"] * t["price"]
        elif t["side"] == "sell":
            positions[sym]["sold"] += t["quantity"]

    # 计算平均成本
    for sym, pos in positions.items():
        if pos["bought"] > 0:
            pos["avg_cost"] = pos["total_cost"] / pos["bought"]
            pos["net_qty"] = pos["bought"] - pos["sold"]
        else:
            pos["net_qty"] = 0

    print("\n" + "=" * 50)
    print("📊 持仓摘要")
    print("=" * 50)
    print(f"\n💰 月收入（税后）：¥{profile['income']['monthly_salary_after_tax']:,.0f}")
    if profile["income"]["monthly_bonus_after_tax"]:
        print(f"   + 奖金（税后）：¥{profile['income']['monthly_bonus_after_tax']:,.0f}")

    total_expenses = sum(profile["expenses"].values())
    print(f"\n📉 月支出：¥{total_expenses:,.0f}")
    print(f"   - 房租/房贷：¥{profile['expenses']['monthly_housing']:,.0f}")
    print(f"   - 贷款还款：¥{profile['expenses']['monthly_loan']:,.0f}")
    print(f"   - 保险：¥{profile['expenses']['monthly_insurance']:,.0f}")
    print(f"   - 生活费：¥{profile['expenses']['monthly_living']:,.0f}")

    monthly_savings = profile["income"]["monthly_salary_after_tax"] + profile["income"]["monthly_bonus_after_tax"] - total_expenses
    print(f"\n💵 月结余：¥{monthly_savings:,.0f}")

    print(f"\n🏦 总资产：¥{(profile['assets']['cash_savings'] or 0):,.0f}")
    print(f"   现金存款：¥{profile['assets']['cash_savings'] or 0:,.0f}")
    print(f"   养老金：¥{profile['assets']['pension'] or 0:,.0f}")

    total_liabilities = sum(profile["liabilities"].values())
    print(f"\n⚠️ 总负债：¥{total_liabilities:,.0f}")
    print(f"   房贷：¥{profile['liabilities']['mortgage'] or 0:,.0f}")
    print(f"   车贷：¥{profile['liabilities']['car_loan'] or 0:,.0f}")

    net_worth = profile["assets"]["cash_savings"] + profile["assets"]["pension"] + profile["assets"]["real_estate"] - total_liabilities
    print(f"\n📈 净资产：¥{net_worth:,.0f}")

    print(f"\n🎯 风险偏好：{profile['risk_preference']}")
    print(f"📌 投资目标：{profile['investment_goal']}")
    print(f"\n📐 目标配置：")
    for asset, pct in profile["target_allocation"].items():
        print(f"   - {asset}：{pct}%")

    print(f"\n📋 当前持仓：")
    if not positions:
        print("   （暂无交易记录）")
    else:
        for sym, pos in positions.items():
            if pos["net_qty"] > 0:
                print(f"   {sym}：{pos['net_qty']:.4f} 股 | 平均成本 ${pos['avg_cost']:.2f}")

    print("=" * 50)


def cmd_rebalance(args):
    """生成再平衡建议"""
    profile = load_profile()
    if not profile:
        print("❌ 财务档案不存在")
        sys.exit(1)

    target = profile["target_allocation"]
    print("\n" + "=" * 50)
    print("⚖️ 再平衡建议")
    print("=" * 50)
    print("\n目标配置：")
    for k, v in target.items():
        print(f"  {k}：{v}%")
    print("\n当前持仓数据需结合实时行情才能计算精确偏离，建议运行 skill 后由 AI 综合分析。")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Portfolio Manager - 投资组合管理")
    sub = parser.add_subparsers()

    p_init = sub.add_parser("init", help="初始化财务档案")
    p_init.add_argument("--salary", type=float, required=True, help="月收入（税后）")
    p_init.add_argument("--bonus", type=float, help="月奖金（税后）")
    p_init.add_argument("--housing", type=float, help="月房租")
    p_init.add_argument("--loan", type=float, help="月贷款还款")
    p_init.add_argument("--insurance", type=float, help="月保险费")
    p_init.add_argument("--living", type=float, default=3000, help="月生活费（默认3000）")
    p_init.add_argument("--cash", type=float, help="现金存款")
    p_init.add_argument("--mortgage", type=float, help="房贷余额")
    p_init.add_argument("--car", type=float, help="车贷余额")
    p_init.add_argument("--risk", default="balanced", choices=["conservative", "balanced", "aggressive"], help="风险偏好")
    p_init.add_argument("--goal", default="retirement", help="投资目标")
    p_init.set_defaults(func=cmd_init)

    p_trade = sub.add_parser("add-trade", help="添加交易记录")
    p_trade.add_argument("--symbol", required=True, help="交易品种代码")
    p_trade.add_argument("--side", required=True, choices=["buy", "sell"], help="买卖方向")
    p_trade.add_argument("--quantity", required=True, help="数量")
    p_trade.add_argument("--price", required=True, help="价格")
    p_trade.add_argument("--date", required=True, help="交易日期 YYYY-MM-DD")
    p_trade.add_argument("--note", help="备注")
    p_trade.set_defaults(func=cmd_add_trade)

    p_upd = sub.add_parser("update-profile", help="更新财务档案")
    p_upd.add_argument("--file", required=True, help="外部JSON文件路径")
    p_upd.set_defaults(func=cmd_update_profile)

    p_sum = sub.add_parser("summary", help="查看持仓摘要")
    p_sum.set_defaults(func=cmd_summary)

    p_rb = sub.add_parser("rebalance", help="生成再平衡建议")
    p_rb.set_defaults(func=cmd_rebalance)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()