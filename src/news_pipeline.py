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

from src.data_fetcher import fetch_newsapi_articles, fetch_finnhub_news

def process_newsapi_data(api_key, keywords):
    """
    Fetches and processes news from NewsAPI.
    """
    all_articles = fetch_newsapi_articles(api_key, keywords)
    if not all_articles:
        # Create dummy data for demonstration if fetch returns empty
        dummy_data = {}
        for keyword in keywords:
            dummy_data[keyword] = [{
                'title': f'This is a sample title about {keyword}',
                'description': 'This is a sample description. The market is volatile.',
                'source': {'name': 'Dummy Source'},
                'publishedAt': pd.Timestamp.now().isoformat(),
                'url': '#',
            }]
        all_articles = dummy_data

    for keyword in all_articles:
        for article in all_articles[keyword]:
            text_to_analyze = f"{article.get('title', '')}. {article.get('description', '')}"
            article['sentiment'] = analyze_sentiment(text_to_analyze)
    return all_articles

def process_finnhub_data(api_key, tickers):
    """
    Fetches and processes news from Finnhub.
    """
    all_news = fetch_finnhub_news(api_key, tickers)
    if not all_news:
        # Create dummy data for demonstration
        dummy_data = {}
        for ticker in tickers:
            dummy_data[ticker] = [{
                'headline': f'Sample headline for {ticker}',
                'summary': 'This is a sample summary. The company reported strong earnings.',
                'source': 'Dummy Source',
                'datetime': pd.Timestamp.now().timestamp(),
                'url': '#',
            }]
        all_news = dummy_data

    for ticker in all_news:
        for item in all_news[ticker]:
            text_to_analyze = f"{item.get('headline', '')}. {item.get('summary', '')}"
            item['sentiment'] = analyze_sentiment(text_to_analyze)
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
    # Process NewsAPI data
    newsapi_data = process_newsapi_data(NEWSAPI_KEY, NEWS_KEYWORDS)
    if newsapi_data:
        save_as_json(newsapi_data, f"{DATA_DIR}/newsapi_articles.json")

    # Process Finnhub data
    finnhub_data = process_finnhub_data(FINNHUB_KEY, FINNHUB_TICKERS)
    if finnhub_data:
        save_as_json(finnhub_data, f"{DATA_DIR}/finnhub_articles.json")

    print("\nNews processing complete.")
