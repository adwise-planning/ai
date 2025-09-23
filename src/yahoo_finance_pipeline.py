import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# --- Configuration ---
DATA_DIR = "../data"
TICKER = "AAPL"
START_DATE = "2020-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")
PARQUET_FILE = os.path.join(DATA_DIR, f"{TICKER}_historical_data.parquet")

# --- Functions ---

def fetch_historical_data(ticker, start_date, end_date):
    """
    Fetches historical stock data from Yahoo Finance.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): The start date for the data in YYYY-MM-DD format.
        end_date (str): The end date for the data in YYYY-MM-DD format.

    Returns:
        pd.DataFrame: A DataFrame containing the historical OHLCV data.
    """
    print(f"Fetching historical data for {ticker} from {start_date} to {end_date}...")
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    print(f"Successfully fetched {len(df)} rows of data.")
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

def update_data(ticker, filepath):
    """
    Updates the historical data with the latest intraday data.

    Args:
        ticker (str): The stock ticker symbol.
        filepath (str): The path to the Parquet file.
    """
    if not os.path.exists(filepath):
        print("No historical data found. Please fetch historical data first.")
        return

    print("Updating data with recent intraday prices...")

    # Load existing data
    existing_df = pd.read_parquet(filepath)

    # Fetch recent data (5-minute interval for the last day)
    recent_df = yf.download(ticker, interval='5m', period='1d', progress=False)

    if isinstance(recent_df.columns, pd.MultiIndex):
        recent_df.columns = recent_df.columns.droplevel(1)

    if recent_df.empty:
        print("No new data found.")
        return

    # Append new data and remove duplicates
    combined_df = pd.concat([existing_df, recent_df])
    combined_df = combined_df[~combined_df.index.duplicated(keep='last')]

    # Save updated data
    save_to_parquet(combined_df, filepath)
    print(f"Data updated. Total rows: {len(combined_df)}")

# --- Main Execution ---

if __name__ == "__main__":
    # 1. Initial data download
    if not os.path.exists(PARQUET_FILE):
        historical_df = fetch_historical_data(TICKER, START_DATE, END_DATE)
        if not historical_df.empty:
            save_to_parquet(historical_df, PARQUET_FILE)
    else:
        print(f"Historical data file already exists at {PARQUET_FILE}. Skipping initial download.")

    # 2. Update with recent data
    update_data(TICKER, PARQUET_FILE)

    # 3. Display sample of the data
    if os.path.exists(PARQUET_FILE):
        final_df = pd.read_parquet(PARQUET_FILE)
        print("\n--- Sample of the final data ---")
        print(final_df.head())
        print("\n--- Data Information ---")
        final_df.info()
