from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta
import pytz
import pandas as pd

from src.plot import plot_pnl_vs_qqq


def make_fake_data(days: int = 260) -> tuple[pd.DataFrame, pd.DataFrame]:
    """先用模拟数据走通流程：后面再替换成 Schwab + Market Data 的真实数据。"""
    tz = pytz.timezone("America/Los_Angeles")
    today = datetime.now(tz).date()

    dates = [today - timedelta(days=i) for i in range(days)][::-1]
    # 只保留工作日（简单模拟交易日）
    dates = [d for d in dates if d.weekday() < 5]

    # 模拟 QQQ 收盘价（随机游走）
    close = []
    price = 400.0
    for i, _ in enumerate(dates):
        price *= (1.0 + (0.001 if i % 3 else -0.0008))  # 假趋势
        close.append(price)

    # 模拟账户每日盈亏（与波动相关的随机形态）
    pnl = []
    for i, _ in enumerate(dates):
        v = (1 if i % 2 == 0 else -1) * (80 + (i % 7) * 25)
        pnl.append(float(v))

    qqq_df = pd.DataFrame({"date": dates, "close": close})
    pnl_df = pd.DataFrame({"date": dates, "pnl": pnl})
    return pnl_df, qqq_df


def write_site(index_path: Path, report_text: str) -> None:
    html = f"""<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Schwab Daily Report</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial; margin: 16px; line-height: 1.5; }}
    .card {{ max-width: 900px; margin: 0 auto; padding: 16px; border: 1px solid #eee; border-radius: 16px; }}
    img {{ width: 100%; height: auto; border-radius: 12px; border: 1px solid #eee; }}
    .muted {{ color:#666; font-size: 14px; }}
    pre {{ white-space: pre-wrap; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Daily Report</h1>
    <div class="muted">Benchmark: QQQ • MA5/MA20/MA250 • (demo data)</div>
    <h2>Chart</h2>
    <img src="pnl_vs_qqq.png" alt="P&L vs QQQ with MAs" />
    <h2>Report</h2>
    <pre>{report_text}</pre>
  </div>
</body>
</html>
"""
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(html, encoding="utf-8")


def main():
    tz = pytz.timezone("America/Los_Angeles")
    now = datetime.now(tz)

    pnl_df, qqq_df = make_fake_data()

    out_png = Path("site/pnl_vs_qqq.png")
    plot_pnl_vs_qqq(pnl_df=pnl_df, qqq_df=qqq_df, out_png=out_png, lookback=180)

    today_pnl = float(pnl_df["pnl"].iloc[-1])
    report = f"""Generated: {now.strftime('%Y-%m-%d %H:%M:%S')} PT
Account Daily P&L: {today_pnl:,.2f} USD

Notes:
- This is DEMO data to validate chart + web pipeline.
- Next step: replace data source with Schwab API + QQQ Market Data.
"""
    write_site(Path("site/index.html"), report)

    print("✅ Generated:")
    print(" - site/pnl_vs_qqq.png")
    print(" - site/index.html")


if __name__ == "__main__":
    main()

