# bot.py

Self-evolving scalper bot for OKX USDT swap markets.

## Features

- Limits concurrent open trades to two.
- Trades with a fixed position size of 50 USDT using 10× leverage (skips orders if free balance is lower).
- Hourly report with trade summary and net PnL.
- Daily report listing net profit/loss per symbol.
- Operates on 15-minute candles by default.
- Automatically closes positions on TP/SL and flattens account if mode changes require it.

