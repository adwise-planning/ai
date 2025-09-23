import streamlit as st

st.set_page_config(
    page_title="Financial Analysis Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Financial Analysis Dashboard")

st.markdown("""
Welcome to the Financial Analysis Dashboard. This dashboard provides a suite of tools for analyzing financial data, including:

- **Credit Risk Analysis**: Explore the Lending Club dataset to understand borrower characteristics and default risk.
- **Market News Sentiment**: Analyze sentiment from financial news sources.
- **Live Crypto Tickers**: (Coming Soon)
- **Portfolio Optimizer**: (Coming Soon)

Use the navigation on the left to explore the different sections of the dashboard.
""")
