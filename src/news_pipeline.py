import os
import json
from newsapi import NewsApiClient
import finnhub
import pandas as pd

# --- Configuration ---
DATA_DIR = "../data"
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "YOUR_NEWSAPI_KEY")
FINNHUB_KEY = os.environ.get("FINNHUB_KEY", "YOUR_FINNHUB_KEY")

# Keywords for NewsAPI
NEWS_KEYWORDS = ["inflation", "Bitcoin", "recession", "S&P500"]

# Tickers for Finnhub
FINNHUB_TICKERS = ["AAPL", "TSLA", "GOOGL"]


# --- Functions ---

def fetch_newsapi_data(api_key, keywords):
    """
    Fetches news articles from NewsAPI for a list of keywords.
    """
    if api_key == "YOUR_NEWSAPI_KEY":
        print("NewsAPI key not set. Skipping NewsAPI fetch.")
        return None

    newsapi = NewsApiClient(api_key=api_key)
    all_articles = {}

    for keyword in keywords:
        print(f"Fetching news for '{keyword}' from NewsAPI...")
        try:
            articles = newsapi.get_everything(
                q=keyword,
                language='en',
                sort_by='relevancy',
                page_size=20  # Keep it small to avoid rate limits
            )
            all_articles[keyword] = articles['articles']
        except Exception as e:
            print(f"Error fetching news for '{keyword}': {e}")
            all_articles[keyword] = []

    return all_articles

def fetch_finnhub_data(api_key, tickers):
    """
    Fetches company news from Finnhub for a list of tickers.
    """
    if api_key == "YOUR_FINNHUB_KEY":
        print("Finnhub key not set. Skipping Finnhub fetch.")
        return None

    finnhub_client = finnhub.Client(api_key=api_key)
    all_news = {}

    for ticker in tickers:
        print(f"Fetching news for '{ticker}' from Finnhub...")
        try:
            # Fetch news for the last 7 days
            today = pd.Timestamp.now().strftime('%Y-%m-%d')
            week_ago = (pd.Timestamp.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
            news = finnhub_client.company_news(ticker, _from=week_ago, to=today)
            all_news[ticker] = news
        except Exception as e:
            print(f"Error fetching news for '{ticker}': {e}")
            all_news[ticker] = []

    return all_news

def save_as_json(data, filepath):
    """
    Saves a dictionary to a JSON file.
    """
    if data:
        print(f"Saving data to {filepath}...")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print("Data saved successfully.")
    else:
        print(f"No data to save for {filepath}.")


# --- Main Execution ---

if __name__ == "__main__":
    # Fetch from NewsAPI
    newsapi_data = fetch_newsapi_data(NEWSAPI_KEY, NEWS_KEYWORDS)
    if newsapi_data:
        save_as_json(newsapi_data, f"{DATA_DIR}/newsapi_articles.json")

    # Fetch from Finnhub
    finnhub_data = fetch_finnhub_data(FINNHUB_KEY, FINNHUB_TICKERS)
    if finnhub_data:
        save_as_json(finnhub_data, f"{DATA_DIR}/finnhub_articles.json")

    print("\nNews fetching process complete.")
