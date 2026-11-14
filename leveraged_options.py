import os
from datetime import date
import pandas as pd
import yfinance as yf
 
GROUPS = {
    "gold": ["GLD", "GDX", "NUGT", "DUST"],
    "nasdaq100": ["^NDX", "QQQ", "QLD", "QID", "TQQQ", "SQQQ"],
    "sp500": ["^SPX", "SPY", "SSO", "SDS", "UPRO", "SPXU"],
    "semis": ["SOXX", "SOXL", "SOXS"],
    "russell2000": ["^RUT", "IWM", "TNA", "TZA"],
}
 
LEVELS = ["^VIX", "^VXN", "^RVX", "^GVZ", "^IRX"]
 
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
    frames = []
    for group, tickers in GROUPS.items():
        for ticker in tickers:
            try:
                frames.append(fetch(group, ticker))
            except Exception as e:
                print(ticker, e)
    df = pd.concat(frames)
    df["snapshot_date"] = today
    df.to_csv(os.path.join(OUT, f"options_{today}.csv.gz"), index=False)
    levels = pd.DataFrame([
        {"ticker": t, "value": yf.Ticker(t).fast_info["last_price"]}
        for t in LEVELS
    ])
    levels["snapshot_date"] = today
    levels.to_csv(os.path.join(OUT, f"levels_{today}.csv"), index=False)
 
 
if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
