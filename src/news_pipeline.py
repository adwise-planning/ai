import os
import json
from newsapi import NewsApiClient
import finnhub
import pandas as pd

import configparser

# --- Configuration ---
config = configparser.ConfigParser()
config.read('config.ini')

DATA_DIR = "data"
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "YOUR_NEWSAPI_KEY")
FINNHUB_KEY = os.environ.get("FINNHUB_KEY", "YOUR_FINNHUB_KEY")

# Keywords for NewsAPI
NEWS_KEYWORDS = [keyword.strip() for keyword in config['news_api']['keywords'].split(',')]

# Tickers for Finnhub
FINNHUB_TICKERS = [ticker.strip() for ticker in config['news_api']['tickers'].split(',')]


# --- Functions ---

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- Functions ---

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text using VADER.
    """
    analyzer = SentimentIntensityAnalyzer()
    if text is None:
        return {}
    return analyzer.polarity_scores(text)

def fetch_newsapi_data(api_key, keywords):
    """
    Fetches news articles from NewsAPI for a list of keywords.
    """
    if api_key == "YOUR_NEWSAPI_KEY":
        print("NewsAPI key not set. Skipping NewsAPI fetch.")
        # Create dummy data for demonstration
        dummy_data = {}
        for keyword in keywords:
            dummy_data[keyword] = [{
                'title': f'This is a sample title about {keyword}',
                'description': 'This is a sample description. The market is volatile.',
                'source': {'name': 'Dummy Source'},
                'publishedAt': pd.Timestamp.now().isoformat(),
                'url': '#',
                'sentiment': analyze_sentiment(f'This is a sample title about {keyword}. This is a sample description. The market is volatile.')
            }]
        return dummy_data


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
            for article in articles['articles']:
                text_to_analyze = f"{article['title']}. {article['description']}"
                article['sentiment'] = analyze_sentiment(text_to_analyze)
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
        # Create dummy data for demonstration
        dummy_data = {}
        for ticker in tickers:
            dummy_data[ticker] = [{
                'headline': f'Sample headline for {ticker}',
                'summary': 'This is a sample summary. The company reported strong earnings.',
                'source': 'Dummy Source',
                'datetime': pd.Timestamp.now().timestamp(),
                'url': '#',
                'sentiment': analyze_sentiment(f'Sample headline for {ticker}. This is a sample summary. The company reported strong earnings.')
            }]
        return dummy_data

    finnhub_client = finnhub.Client(api_key=api_key)
    all_news = {}

    for ticker in tickers:
        print(f"Fetching news for '{ticker}' from Finnhub...")
        try:
            # Fetch news for the last 7 days
            today = pd.Timestamp.now().strftime('%Y-%m-%d')
            week_ago = (pd.Timestamp.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
            news = finnhub_client.company_news(ticker, _from=week_ago, to=today)
            for item in news:
                text_to_analyze = f"{item['headline']}. {item['summary']}"
                item['sentiment'] = analyze_sentiment(text_to_analyze)
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
