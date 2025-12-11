import time
import datetime as dt
from typing import Optional, List, Tuple

import requests
import pandas as pd


COINBASE_BASE_URL = "https://api.exchange.coinbase.com"
PRODUCT_ID = "ETH-USD"   


def _iso_to_timestamp(iso_str: str) -> int:
    """Convert ISO 8601 string to UNIX timestamp (seconds)."""
    return int(dt.datetime.fromisoformat(iso_str.replace("Z", "+00:00")).timestamp())


def _timestamp_to_iso(ts: int) -> str:
    """Convert UNIX timestamp (seconds) to ISO 8601 string."""
    return dt.datetime.utcfromtimestamp(ts).isoformat() + "Z"


def fetch_coinbase_candles(
    start_iso: str,
    end_iso: str,
    granularity: int = 60,
    product_id: str = PRODUCT_ID,
    max_batch_size: int = 300,
    sleep_seconds: float = 0.2,
) -> pd.DataFrame:

    start_ts = _iso_to_timestamp(start_iso)
    end_ts = _iso_to_timestamp(end_iso)
    if end_ts <= start_ts:
        raise ValueError("end_iso must be after start_iso")

    rows: List[Tuple[int, float, float, float, float, float]] = []

    url = f"{COINBASE_BASE_URL}/products/{product_id}/candles"

    batch_span = granularity * max_batch_size

    current_start = start_ts

    while current_start < end_ts:
        current_end = min(current_start + batch_span, end_ts)

        params = {
            "start": _timestamp_to_iso(current_start),
            "end": _timestamp_to_iso(current_end),
            "granularity": granularity,
        }

        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            raise RuntimeError(
                f"Coinbase API error {resp.status_code}: {resp.text}"
            )

        data = resp.json()

        for entry in data:
            ts, low, high, open_, close, volume = entry
            rows.append((ts, open_, high, low, close, volume))

        current_start = current_end
        time.sleep(sleep_seconds)

    if not rows:
        return pd.DataFrame(
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

    df = pd.DataFrame(
        rows,
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    ).drop_duplicates(subset="timestamp")

    df = df.sort_values("timestamp")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df.set_index("timestamp", inplace=True)

    return df


if __name__ == "__main__":
    start = "2021-05-05T00:00:00Z"
    end = "2023-05-05T00:00:00Z"
    gran = 60  

    print(f"Fetching Coinbase {PRODUCT_ID} candles from {start} to {end}, gran={gran}s...")
    df_candles = fetch_coinbase_candles(start, end, granularity=gran)
    df_candles.to_csv("../../data/raw/coinbase_candles.csv" )
    print(df_candles.head())
    print(df_candles.tail())
    print("Total candles fetched:", len(df_candles))

