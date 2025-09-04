# bot.py

Self-evolving scalper bot for OKX USDT swap markets.

## Features

- Limits concurrent open trades to two.
- Trades always use a hard‑coded 50 USDT margin at 10× leverage (~500 USDT notional; order is skipped if free balance is lower).
- Converts order sizes using OKX contract multipliers so each fill equals roughly 500 USDT notional.
- Hourly report with trade summary and net PnL.
- Daily report listing net profit/loss per symbol.
- Operates on 15-minute candles by default.
- Automatically closes positions on TP/SL and flattens account if mode changes require it, skipping mode changes when open trades remain.

