import streamlit as st
import json
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(
    page_title="News Sentiment",
    page_icon="📰",
    layout="wide",
)

import os

# --- Load Data ---
@st.cache_data
def load_news_data(filename):
    """
    Loads news data from a JSON file.
    """
    # Construct a robust path to the data file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    filepath = os.path.join(project_root, "data", filename)

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None

newsapi_data = load_news_data("newsapi_articles.json")
finnhub_data = load_news_data("finnhub_articles.json")


# --- Main Dashboard ---
st.title("📰 News Sentiment Analysis")

st.markdown("""
This page displays financial news from NewsAPI and Finnhub.
*Note: This demo runs with placeholder API keys. To fetch live data, please set your API keys in `src/news_pipeline.py` and run the script.*
""")


import plotly.express as px

# --- NewsAPI Section ---
st.header("General Market News (from NewsAPI)")
if newsapi_data:
    all_headlines = []
    all_articles_list = []
    for keyword, articles in newsapi_data.items():
        for article in articles:
            article['keyword'] = keyword
            all_articles_list.append(article)

    if all_articles_list:
        df_newsapi = pd.DataFrame(all_articles_list)
        df_newsapi['sentiment_compound'] = df_newsapi['sentiment'].apply(lambda x: x.get('compound', 0))

        # --- Sentiment Chart ---
        avg_sentiment_newsapi = df_newsapi.groupby('keyword')['sentiment_compound'].mean().reset_index()
        fig_newsapi = px.bar(avg_sentiment_newsapi, x='keyword', y='sentiment_compound', title='Average Sentiment by Keyword', color='keyword')
        st.plotly_chart(fig_newsapi, use_container_width=True)

        # --- Articles ---
        for keyword, articles in newsapi_data.items():
            st.subheader(f"Keyword: {keyword}")
            if articles:
                for article in articles:
                    st.write(f"**{article['title']}**")
                    st.write(f"_{article['source']['name']}_ - {pd.to_datetime(article['publishedAt']).strftime('%Y-%m-%d')}")
                    st.write(article['description'])
                    sentiment = article.get('sentiment', {})
                    st.write(f"**Sentiment:** Compound: `{sentiment.get('compound', 0):.2f}`, "
                             f"Positive: `{sentiment.get('pos', 0):.2f}`, "
                             f"Negative: `{sentiment.get('neg', 0):.2f}`")
                    st.write(f"[Read more]({article['url']})")
                    st.markdown("---")
                    all_headlines.append(article['title'])
            else:
                st.write("No articles found for this keyword.")

        # Word Cloud
        if all_headlines:
            st.subheader("Headlines Word Cloud")
            text = " ".join(all_headlines)
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

else:
    st.warning("NewsAPI data not found. Run `python src/news_pipeline.py` to fetch it.")


# --- Finnhub Section ---
st.header("Company-Specific News (from Finnhub)")
if finnhub_data:
    all_finnhub_list = []
    for ticker, news_items in finnhub_data.items():
        for item in news_items:
            item['ticker'] = ticker
            all_finnhub_list.append(item)

    if all_finnhub_list:
        df_finnhub = pd.DataFrame(all_finnhub_list)
        df_finnhub['sentiment_compound'] = df_finnhub['sentiment'].apply(lambda x: x.get('compound', 0))

        # --- Sentiment Chart ---
        avg_sentiment_finnhub = df_finnhub.groupby('ticker')['sentiment_compound'].mean().reset_index()
        fig_finnhub = px.bar(avg_sentiment_finnhub, x='ticker', y='sentiment_compound', title='Average Sentiment by Ticker', color='ticker')
        st.plotly_chart(fig_finnhub, use_container_width=True)

        # --- Articles ---
        for ticker, news_items in finnhub_data.items():
            st.subheader(f"Ticker: {ticker}")
            if news_items:
                for item in news_items:
                    st.write(f"**{item['headline']}**")
                    st.write(f"_{item['source']}_ - {pd.to_datetime(item['datetime'], unit='s').strftime('%Y-%m-%d')}")
                    st.write(item['summary'])
                    sentiment = item.get('sentiment', {})
                    st.write(f"**Sentiment:** Compound: `{sentiment.get('compound', 0):.2f}`, "
                             f"Positive: `{sentiment.get('pos', 0):.2f}`, "
                             f"Negative: `{sentiment.get('neg', 0):.2f}`")
                    st.write(f"[Read more]({item['url']})")
                    st.markdown("---")
            else:
                st.write("No news found for this ticker.")
else:
    st.warning("Finnhub data not found. Run `python src/news_pipeline.py` to fetch it.")
