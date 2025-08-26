# Paper Trading Bot

سكربت بايثون بسيط للتداول الورقي يحتوي على:

- تنبيهات وسجلات CSV.
- مولد أدوات جديد وإدارة مخاطر مطورة.
- استراتيجيات modular يسهل إضافتها أو حذفها.
- إمكانية إجراء Backtest سريع على البيانات التاريخية.
- Kill switch لمسح جميع المراكز الورقية.

تشغيل backtest:

```bash
python bot.py --backtest data.csv
```

حيث يحتوي `data.csv` على أعمدة `open,high,low,close`.

لتفعيل kill switch:

```bash
python bot.py --killswitch
```
