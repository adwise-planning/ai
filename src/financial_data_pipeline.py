import os
import pandas as pd
import configparser
from datetime import datetime
from binance.client import Client

from src.data_fetcher import fetch_yfinance_data, fetch_binance_klines
import pandas_ta as ta

# --- Configuration ---
config = configparser.ConfigParser()
config.read('config.ini')

DATA_DIR = "data"
YAHOO_TICKERS = [ticker.strip() for ticker in config['yahoo_finance']['tickers'].split(',')]
BINANCE_TICKERS = [ticker.strip() for ticker in config['binance']['tickers'].split(',')]
START_DATE = "2020-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

# --- Processing Functions ---
def add_technical_indicators(df):
    """
    Adds technical indicators to the DataFrame.
    """
    print("Adding technical indicators (RSI, MACD, Bollinger Bands)...")
    df.ta.rsi(append=True)
    df.ta.macd(append=True)
    df.ta.bbands(append=True)
    print("Technical indicators added.")
    return df

def save_to_parquet(df, filepath):
    """
    Saves a DataFrame to a Parquet file.
    """
    print(f"Saving data to {filepath}...")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_parquet(filepath)
    print("Data saved successfully.")

# --- Main Execution ---
if __name__ == "__main__":
    # Process Yahoo Finance Tickers
    for ticker in YAHOO_TICKERS:
        print(f"\n--- Processing Yahoo Finance ticker: {ticker} ---")
        filepath = os.path.join(DATA_DIR, f"{ticker.replace('^', '')}_historical_data.parquet")

        df = fetch_yfinance_data(ticker, START_DATE, END_DATE)
        if not df.empty:
            processed_df = add_technical_indicators(df)
            save_to_parquet(processed_df, filepath)
        else:
            print(f"No data fetched for {ticker}.")

    # Process Binance Tickers
    for ticker in BINANCE_TICKERS:
        print(f"\n--- Processing Binance ticker: {ticker} ---")
        filepath = os.path.join(DATA_DIR, f"{ticker}_1h_historical_data.parquet")

        df = fetch_binance_klines(ticker, Client.KLINE_INTERVAL_1HOUR, START_DATE)
        if not df.empty:
            processed_df = add_technical_indicators(df)
            save_to_parquet(processed_df, filepath)
        else:
            print(f"No data fetched for {ticker}.")

    print("\n--- Financial data processing complete ---")
