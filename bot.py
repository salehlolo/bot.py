#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper trading bot مع خصائص:
- تنبيهات وسجلات CSV.
- مولد أدوات بسيط + إدارة مخاطر مطورة.
- استراتيجيات modular تقدر تضيف/تحذف بسهولة.
- إمكانية عمل Backtest بسرعة على البيانات التاريخية.
- Kill switch يمسح كل المراكز الورقية.
"""

import argparse
import csv
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# =========================
# Tool Generator
# =========================

class ToolGenerator:
    """مولد أدوات بسيط لحساب المؤشرات"""

    @staticmethod
    def moving_average(prices: List[float], period: int) -> List[Optional[float]]:
        ma: List[Optional[float]] = []
        for i in range(len(prices)):
            if i + 1 < period:
                ma.append(None)
            else:
                window = prices[i + 1 - period : i + 1]
                ma.append(sum(window) / period)
        return ma

# =========================
# Risk Management
# =========================

@dataclass
class RiskManager:
    balance: float = 10_000.0
    risk_per_trade: float = 0.01  # 1%
    max_positions: int = 3

    def size(self, price: float) -> float:
        usd = self.balance * self.risk_per_trade
        return usd / price if price else 0.0

# =========================
# Strategies
# =========================

class Strategy:
    """أساس أي إستراتيجية"""
    name: str = "base"

    def on_data(self, idx: int, row: Dict[str, float], ctx: Dict[str, Any]) -> Optional[str]:
        return None

class MovingAverageCross(Strategy):
    name = "ma_cross"

    def __init__(self, fast: int = 5, slow: int = 20):
        self.fast = fast
        self.slow = slow

    def on_data(self, idx: int, row: Dict[str, float], ctx: Dict[str, Any]) -> Optional[str]:
        fast_ma = ctx["fast_ma"][idx]
        slow_ma = ctx["slow_ma"][idx]
        position = ctx.get("position")
        if fast_ma is None or slow_ma is None:
            return None
        if fast_ma > slow_ma and position is None:
            return "buy"
        if fast_ma < slow_ma and position == "long":
            return "exit"
        return None

# =========================
# Paper Trading Account
# =========================

@dataclass
class Position:
    id: int
    symbol: str
    side: str
    entry: float
    qty: float

@dataclass
class PaperAccount:
    csv_file: str = "trades.csv"
    positions: List[Position] = field(default_factory=list)
    _next_id: int = 1

    def open(self, symbol: str, side: str, price: float, qty: float) -> Position:
        pos = Position(self._next_id, symbol, side, price, qty)
        self.positions.append(pos)
        self._next_id += 1
        self._log("OPEN", pos, price, 0.0)
        return pos

    def close(self, pos: Position, price: float) -> float:
        pnl = (price - pos.entry) * pos.qty * (1 if pos.side == "long" else -1)
        self.positions.remove(pos)
        self._log("CLOSE", pos, price, pnl)
        return pnl

    def kill_switch(self) -> None:
        self.positions.clear()

    def _log(self, action: str, pos: Position, price: float, pnl: float) -> None:
        exists = os.path.exists(self.csv_file)
        with open(self.csv_file, "a", newline="") as f:
            w = csv.writer(f)
            if not exists:
                w.writerow(["ts", "action", "id", "symbol", "side", "qty", "price", "pnl"])
            w.writerow([int(time.time()), action, pos.id, pos.symbol, pos.side, pos.qty, price, pnl])

# =========================
# Bot
# =========================

class PaperTradingBot:
    def __init__(self):
        self.account = PaperAccount()
        self.strategies: List[Strategy] = []
        self.risk = RiskManager()

    # إدارة الاستراتيجيات
    def add_strategy(self, strat: Strategy) -> None:
        self.strategies.append(strat)

    def remove_strategy(self, name: str) -> None:
        self.strategies = [s for s in self.strategies if s.name != name]

    # تنبيه بسيط
    def alert(self, msg: str) -> None:
        print(msg)

    # kill switch
    def kill_switch(self) -> None:
        self.account.kill_switch()
        self.alert("⚠️ Kill switch activated – all paper positions cleared")

    # Backtesting
    def backtest(self, data: List[Dict[str, float]]) -> List[float]:
        closes = [d["close"] for d in data]
        ctx = {
            "closes": closes,
            "fast_ma": ToolGenerator.moving_average(closes, 5),
            "slow_ma": ToolGenerator.moving_average(closes, 20),
            "position": None,
        }
        pos: Optional[Position] = None
        pnls: List[float] = []
        for i, row in enumerate(data):
            ctx["position"] = "long" if pos else None
            for strat in self.strategies:
                sig = strat.on_data(i, row, ctx)
                if sig == "buy" and pos is None and len(self.account.positions) < self.risk.max_positions:
                    qty = self.risk.size(row["close"])
                    pos = self.account.open("TEST", "long", row["close"], qty)
                    self.alert(f"🔔 BUY {row['close']:.2f}")
                elif sig == "exit" and pos is not None:
                    pnl = self.account.close(pos, row["close"])
                    pnls.append(pnl)
                    self.alert(f"💰 EXIT {row['close']:.2f} PnL={pnl:.2f}")
                    pos = None
        return pnls

# =========================
# Utilities
# =========================

def load_csv(path: str) -> List[Dict[str, float]]:
    with open(path) as f:
        reader = csv.DictReader(f)
        return [
            {k: float(row[k]) for k in ["open", "high", "low", "close"]}
            for row in reader
        ]

# =========================
# CLI
# =========================

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simple modular paper trading bot")
    p.add_argument("--backtest", help="ملف CSV يحتوي على بيانات OHLC")
    p.add_argument("--killswitch", action="store_true", help="يمسح كل المراكز الورقية")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    bot = PaperTradingBot()
    bot.add_strategy(MovingAverageCross())

    if args.killswitch:
        bot.kill_switch()
        return

    if args.backtest:
        data = load_csv(args.backtest)
        bot.backtest(data)
        return

    print("لا يوجد أمر. استخدم --backtest أو --killswitch")

if __name__ == "__main__":
    main()
