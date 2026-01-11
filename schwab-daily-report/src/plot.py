from __future__ import annotations
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

MA_DAY = 5
MA_MONTH = 20
MA_YEAR = 250

def plot_pnl_vs_qqq(pnl_df: pd.DataFrame, qqq_df: pd.DataFrame, out_png: Path, lookback: int = 180) -> None:
    pnl_df = pnl_df.copy()
    qqq_df = qqq_df.copy()

    pnl_df["date"] = pd.to_datetime(pnl_df["date"])
    qqq_df["date"] = pd.to_datetime(qqq_df["date"])

    pnl_df = pnl_df.sort_values("date").dropna()
    qqq_df = qqq_df.sort_values("date").dropna()

    df = pd.merge(qqq_df, pnl_df, on="date", how="inner").tail(lookback)

    df["ma_day"] = df["close"].rolling(MA_DAY).mean()
    df["ma_month"] = df["close"].rolling(MA_MONTH).mean()
    df["ma_year"] = df["close"].rolling(MA_YEAR).mean()

    # X 轴标签
    x = df["date"].dt.strftime("%m-%d")

    # 柱子颜色（赚绿亏红）
    colors = ["#2ca02c" if v >= 0 else "#d62728" for v in df["pnl"].fillna(0)]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.bar(x, df["pnl"], color=colors, alpha=0.75, label="Daily P&L ($)")
    ax1.set_ylabel("Daily P&L ($)")
    ax1.tick_params(axis="x", rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(x, df["close"], linewidth=1.6, label="QQQ Close")
    ax2.plot(x, df["ma_day"], linewidth=1.1, linestyle="--", label=f"MA{MA_DAY}")
    ax2.plot(x, df["ma_month"], linewidth=1.1, linestyle="--", label=f"MA{MA_MONTH}")
    ax2.plot(x, df["ma_year"], linewidth=1.1, linestyle="--", label=f"MA{MA_YEAR}")
    ax2.set_ylabel("QQQ Price")

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, loc="upper left")

    plt.title("Daily P&L vs QQQ (MA Day/Month/Year)")
    plt.tight_layout()

    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=200)
    plt.close(fig)
