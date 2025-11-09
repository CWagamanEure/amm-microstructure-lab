import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone
import argparse


def get_mid_history_from_candles(product_id, start, end, granularity=60):
    '''
    Approximate the historical mid using (high+low)/2 from candles.
    '''
    params = {
        "start": start,
        "end": end,
        "granularity": granularity
    }

    r = requests.get(f"https://api.exchange.coinbase.com/products/{product_id}/candles", params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    out = []

    for t, low, high, _open, close, vol in data:
        mid = (low + high) /2
        ts = datetime
        out.append({"ts": ts, "mid": mid, "low": low, "high": high, "close": close, "vol": vol})
    out.sort(key=lambda x: x["ts"])
    return out


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tickerPair", default="ETH-USD")
    parser.add_argument("-s", "--start", default="2021-05-01")
    parser.add_argument("-e", "--end", default="2023-05-01")


    args = parser.parse_args()

    out = get_mid_history_from_candles(args.tickerPair, args.start, args.end)
    df = pd.DataFrame(out)
    df.to_csv("../../data/raw/{tickerPair}_CEX_data.csv")

