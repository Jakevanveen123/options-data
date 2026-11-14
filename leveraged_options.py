import os
from datetime import date
import pandas as pd
import yfinance as yf

GROUPS = {
    "gold_miners": ["GDX", "NUGT", "DUST"],
    "nasdaq100": ["QQQ", "TQQQ", "SQQQ"],
    "sp500": ["SPY", "UPRO", "SPXU"],
    "semis": ["SOXX", "SOXL", "SOXS"],
    "russell2000": ["IWM", "TNA", "TZA"],
}

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def fetch(group, ticker):
    tk = yf.Ticker(ticker)
    spot = tk.fast_info["last_price"]
    frames = []
    for exp in tk.options:
        chain = tk.option_chain(exp)
        for kind, df in [("call", chain.calls), ("put", chain.puts)]:
            frames.append(df.assign(
                group=group,
                underlying=ticker,
                spot=spot,
                expiry=exp,
                type=kind,
            ))
    return pd.concat(frames)


def main():
    today = date.today().isoformat()
    os.makedirs(OUT, exist_ok=True)
    df = pd.concat([
        fetch(group, ticker)
        for group, tickers in GROUPS.items()
        for ticker in tickers
    ])
    df["snapshot_date"] = today
    df.to_csv(os.path.join(OUT, f"options_{today}.csv"), index=False)


if __name__ == "__main__":
    main()
