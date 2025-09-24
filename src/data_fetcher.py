import yfinance as yf
import pandas as pd
import os
from datetime import datetime
from binance.client import Client
from newsapi import NewsApiClient
import finnhub
import pandas_datareader.data as web
import subprocess
import configparser

# --- Configuration ---
config = configparser.ConfigParser()
config.read('config.ini')

# --- Yahoo Finance Fetcher ---
def fetch_yfinance_data(ticker, start_date, end_date):
    """
    Fetches historical stock data from Yahoo Finance.
    """
    print(f"Fetching historical data for {ticker} from {start_date} to {end_date}...")
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    print(f"Successfully fetched {len(df)} rows of data for {ticker}.")
    return df

# --- Binance Fetcher ---
def fetch_binance_klines(symbol, interval, start_str):
    """
    Fetch historical klines from Binance.
    """
    client = Client(tld='us')
    start_ts = int(datetime.strptime(start_str, "%Y-%m-%d").timestamp() * 1000)
    print(f"Fetching klines for {symbol} from {start_str}...")
    klines = []
    while True:
        new_klines = client.get_historical_klines(symbol, interval, start_ts, limit=1000)
        if not new_klines:
            break
        klines.extend(new_klines)
        start_ts = new_klines[-1][0] + 1
        # time.sleep(0.1) # This can be uncommented if rate limits are an issue
    print(f"Fetched a total of {len(klines)} klines for {symbol}.")
    if not klines:
        return pd.DataFrame()
    df = pd.DataFrame(klines, columns=[
        'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close time', 'Quote asset volume', 'Number of trades',
        'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
    ])
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col])
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df.set_index('Open time', inplace=True)
    df = df.drop(['Close time', 'Ignore', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume'], axis=1)
    return df

# --- NewsAPI Fetcher ---
def fetch_newsapi_articles(api_key, keywords):
    """
    Fetches news articles from NewsAPI for a list of keywords.
    """
    if api_key == "YOUR_NEWSAPI_KEY":
        print("NewsAPI key not set. Returning empty data for NewsAPI.")
        return {}
    newsapi = NewsApiClient(api_key=api_key)
    all_articles = {}
    for keyword in keywords:
        print(f"Fetching news for '{keyword}' from NewsAPI...")
        try:
            articles = newsapi.get_everything(q=keyword, language='en', sort_by='relevancy', page_size=20)
            all_articles[keyword] = articles['articles']
        except Exception as e:
            print(f"Error fetching news for '{keyword}': {e}")
            all_articles[keyword] = []
    return all_articles

# --- Finnhub Fetcher ---
def fetch_finnhub_news(api_key, tickers):
    """
    Fetches company news from Finnhub for a list of tickers.
    """
    if api_key == "YOUR_FINNHUB_KEY":
        print("Finnhub key not set. Returning empty data for Finnhub.")
        return {}
    finnhub_client = finnhub.Client(api_key=api_key)
    all_news = {}
    for ticker in tickers:
        print(f"Fetching news for '{ticker}' from Finnhub...")
        try:
            today = pd.Timestamp.now().strftime('%Y-%m-%d')
            week_ago = (pd.Timestamp.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
            news = finnhub_client.company_news(ticker, _from=week_ago, to=today)
            all_news[ticker] = news
        except Exception as e:
            print(f"Error fetching news for '{ticker}': {e}")
            all_news[ticker] = []
    return all_news

# --- FRED Fetcher ---
def fetch_fred_data(series_id, start_date, end_date):
    """
    Fetches economic data from FRED.
    """
    print(f"Fetching data for {series_id} from FRED...")
    try:
        df = web.DataReader(series_id, "fred", start_date, end_date)
        print(f"Successfully fetched {len(df)} rows for {series_id}.")
        return df
    except Exception as e:
        print(f"Error fetching data from FRED: {e}")
        return pd.DataFrame()

# --- Kaggle Fetcher ---
def download_from_kaggle(dataset, filename, data_dir):
    """
    Attempts to download a specific file from a Kaggle dataset.
    """
    print("--- Attempting to download data from Kaggle ---")
    raw_data_file = os.path.join(data_dir, filename)
    if os.path.exists(raw_data_file):
        print(f"Data file already exists at {raw_data_file}. Skipping download.")
        return True
    try:
        subprocess.run(
            ["kaggle", "datasets", "download", "-d", dataset, "-f", filename, "-p", data_dir, "--unzip"],
            check=True, capture_output=True, text=True
        )
        print("Successfully downloaded data from Kaggle.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("!!! WARNING: Failed to download from Kaggle. !!!")
        if isinstance(e, subprocess.CalledProcessError):
            print(f"Kaggle API error: {e.stderr}")
        else:
            print("It seems the 'kaggle' command is not installed or not in your PATH.")
        return False
