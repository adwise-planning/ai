import os
import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta
import time

# --- Configuration ---
DATA_DIR = "../data"
SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_1HOUR
START_DATE = "2020-01-01"
PARQUET_FILE = os.path.join(DATA_DIR, f"{SYMBOL}_{INTERVAL}_historical_data.parquet")

# --- Functions ---

def fetch_historical_klines(symbol, interval, start_str):
    """
    Fetch historical klines from Binance.

    :param symbol: Name of symbol 'BTCUSDT'
    :param interval: Klines interval - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    :param start_str: From date in 'YYYY-MM-DD' format
    :return: pandas DataFrame with historical klines
    """
    client = Client(tld='us')

    # Calculate start timestamp
    start_ts = int(datetime.strptime(start_str, "%Y-%m-%d").timestamp() * 1000)

    print(f"Fetching klines for {symbol} from {start_str}...")

    # Get all klines from start_ts up to now
    klines = []
    while True:
        # Fetch klines from Binance
        new_klines = client.get_historical_klines(symbol, interval, start_ts, limit=1000)

        # If no klines are returned, we are done
        if not new_klines:
            break

        # Add the new klines to our list
        klines.extend(new_klines)

        # Update the start timestamp to the last kline's open time + 1ms
        start_ts = new_klines[-1][0] + 1

        # Small delay to avoid hitting API rate limits
        time.sleep(0.1)

    print(f"Fetched a total of {len(klines)} klines for {symbol}.")

    # Create a pandas DataFrame
    df = pd.DataFrame(klines, columns=[
        'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close time', 'Quote asset volume', 'Number of trades',
        'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
    ])

    # Convert columns to numeric
    for col in ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote asset volume', 'Taker buy base asset volume', 'Taker buy quote asset volume']:
        df[col] = pd.to_numeric(df[col])

    # Convert timestamp to datetime and set as index
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df.set_index('Open time', inplace=True)

    # Drop unnecessary columns
    df = df.drop(['Close time', 'Ignore', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume'], axis=1)

    return df

def save_to_parquet(df, filepath):
    """
    Saves a DataFrame to a Parquet file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        filepath (str): The path to the Parquet file.
    """
    print(f"Saving data to {filepath}...")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_parquet(filepath)
    print("Data saved successfully.")


# --- Main Execution ---

if __name__ == "__main__":
    if not os.path.exists(PARQUET_FILE):
        print(f"File {PARQUET_FILE} not found, fetching historical data...")
        btc_df = fetch_historical_klines(SYMBOL, INTERVAL, START_DATE)
        if not btc_df.empty:
            save_to_parquet(btc_df, PARQUET_FILE)
        else:
            print("No data fetched.")
    else:
        print(f"File {PARQUET_FILE} already exists. Skipping download.")

    if os.path.exists(PARQUET_FILE):
        final_df = pd.read_parquet(PARQUET_FILE)
        print("\n--- Sample of the final data ---")
        print(final_df.head())
        print("\n--- Data Information ---")
        final_df.info()
