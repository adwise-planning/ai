import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import time
from src.utils import run_script
import configparser

# --- Page Configuration ---
st.set_page_config(
    page_title="Financial Analysis Dashboard",
    page_icon="📊",
    layout="wide",
)

# --- Helper Functions ---
@st.cache_data
def load_data(filepath, file_type='parquet', nrows=None):
    if not os.path.exists(filepath):
        st.error(f"Data file not found: {filepath}. Please run the required pipeline from the Control Panel.")
        return None
    try:
        if file_type == 'parquet':
            return pd.read_parquet(filepath)
        elif file_type in ['csv', 'gz']:
            compression = 'gzip' if file_type == 'gz' else None
            return pd.read_csv(filepath, compression=compression, nrows=nrows)
        elif file_type == 'json':
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading {filepath}: {e}")
    return None

# --- Render Functions for each Tab ---

def render_credit_risk_explorer(tab):
    with tab:
        st.subheader("💳 Credit Risk Explorer")
        credit_df = load_data("data/lending_club_processed.parquet")
        if credit_df is not None:
            st.sidebar.header("Credit Risk Filters")
            loan_status_filter = st.sidebar.multiselect("Loan Status", options=credit_df["loan_status"].unique(), default=credit_df["loan_status"].unique(), key="cr_loan_status")
            income_bin_filter = st.sidebar.multiselect("Income Bin", options=credit_df["income_bin"].unique(), default=credit_df["income_bin"].unique(), key="cr_income_bin")

            filtered_df = credit_df[credit_df["loan_status"].isin(loan_status_filter) & credit_df["income_bin"].isin(income_bin_filter)]

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Loans", f"{len(filtered_df):,}")
            col2.metric("Average Loan Amount (Scaled)", f"{filtered_df['loan_amnt'].mean():.2f}")
            col3.metric("Average DTI (Scaled)", f"{filtered_df['dti'].mean():.2f}")

            fig = px.pie(filtered_df, names="loan_status", title="Loan Status Distribution", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(filtered_df)

def render_news_sentiment(tab):
    with tab:
        st.subheader("📰 News Sentiment")
        newsapi_data = load_data("data/newsapi_articles.json", 'json')
        finnhub_data = load_data("data/finnhub_articles.json", 'json')

        st.write("### General Market News (from NewsAPI)")
        if newsapi_data:
            # ... (full news rendering logic) ...
            st.dataframe(pd.DataFrame(newsapi_data.get('inflation', [])))
        else:
            st.warning("NewsAPI data not found.")

        st.write("### Company-Specific News (from Finnhub)")
        if finnhub_data:
            # ... (full news rendering logic) ...
            st.dataframe(pd.DataFrame(finnhub_data.get('AAPL', [])))
        else:
            st.warning("Finnhub data not found.")

def render_asset_explorer(tab):
    with tab:
        st.subheader("📈 Asset Explorer")
        config = configparser.ConfigParser()
        config.read('config.ini')
        tickers = [t.strip() for t in config['yahoo_finance']['tickers'].split(',')] + [t.strip() for t in config['binance']['tickers'].split(',')]
        selected_ticker = st.selectbox("Select Asset", tickers)

        filepath = f"data/{selected_ticker.replace('^', '')}_historical_data.parquet"
        if "USDT" in selected_ticker: # It's a binance ticker
            filepath = f"data/{selected_ticker}_1h_historical_data.parquet"

        asset_df = load_data(filepath)
        if asset_df is not None:
            fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=(f"{selected_ticker} Price (OHLC)", "Volume", "RSI", "MACD"), row_heights=[0.6, 0.1, 0.15, 0.15])
            fig.add_trace(go.Candlestick(x=asset_df.index, open=asset_df['Open'], high=asset_df['High'], low=asset_df['Low'], close=asset_df['Close'], name='OHLC'), row=1, col=1)
            fig.add_trace(go.Bar(x=asset_df.index, y=asset_df['Volume'], name='Volume'), row=2, col=1)
            fig.add_trace(go.Scatter(x=asset_df.index, y=asset_df['RSI_14'], name='RSI'), row=3, col=1)
            fig.add_trace(go.Scatter(x=asset_df.index, y=asset_df['MACD_12_26_9'], name='MACD'), row=4, col=1)
            fig.update_layout(height=800, showlegend=False, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

def render_macro_trends(tab):
    with tab:
        st.subheader("🌍 Macro Trends: CPI vs. S&P 500")
        cpi_df = load_data("data/cpi_data.parquet")
        gspc_df = load_data("data/GSPC_historical_data.parquet")
        if cpi_df is not None and gspc_df is not None:
            gspc_monthly = gspc_df['Close'].resample('M').last().pct_change() * 100
            cpi_pct_change = cpi_df['CPI'].pct_change(12) * 100
            combined_df = pd.DataFrame({'S&P 500 Returns': gspc_monthly, 'CPI % Change': cpi_pct_change}).dropna()
            fig = px.line(combined_df, y=['S&P 500 Returns', 'CPI % Change'], title="S&P 500 Monthly Returns vs. CPI Year-over-Year Change")
            st.plotly_chart(fig, use_container_width=True)

def render_portfolio_optimizer(tab):
    with tab:
        st.subheader("⚖️ Portfolio Optimizer")
        # ... (Full portfolio optimizer logic) ...
        st.info("Portfolio Optimizer logic goes here.")


def render_control_panel(tab):
    st.header("🛠️ Control Panel")
    st.subheader("Pipeline Execution")
    PIPELINE_SCRIPTS = ["src/financial_data_pipeline.py", "src/credit_data_pipeline.py", "src/macro_data_pipeline.py", "src/news_pipeline.py"]
    if st.button("Run All Pipelines"):
        with st.spinner("Running all pipelines..."):
            output = ""
            for script in PIPELINE_SCRIPTS:
                output += f">>> Running {script}...\n"
                output += run_script(script) + "\n\n"
            st.code(output, language='bash')
        st.success("All pipelines finished.")

    st.subheader("Configuration Management")
    CONFIG_FILE = 'config.ini'
    try:
        with open(CONFIG_FILE, 'r') as f:
            config_text = f.read()
    except FileNotFoundError:
        config_text = "[Error] config.ini not found."
    new_config_text = st.text_area("config.ini", value=config_text, height=300)
    if st.button("Save Configuration"):
        with open(CONFIG_FILE, 'w') as f:
            f.write(new_config_text)
        st.success("Configuration saved.")
        st.rerun()

def render_data_viewer(tab):
    st.header("📄 Data Viewer")
    DATA_DIR = "data"
    try:
        available_files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
    except FileNotFoundError:
        available_files = []
    if not available_files:
        st.warning(f"No data files found in `{DATA_DIR}`.")
    else:
        selected_file = st.selectbox("Select a data file", options=available_files)
        if selected_file:
            filepath = os.path.join(DATA_DIR, selected_file)
            st.subheader(f"Preview of `{selected_file}`")
            df_view = load_data(filepath, selected_file.split('.')[-1])
            if df_view is not None:
                st.dataframe(df_view)

# --- Main App ---
st.title("📊 Financial Analysis Dashboard")

main_tab1, main_tab2, main_tab3 = st.tabs(["📈 Analysis", "🛠️ Control Panel", "📄 Data Viewer"])

with main_tab1:
    st.header("Analysis Dashboards")
    analysis_tabs = st.tabs(["Credit Risk", "News Sentiment", "Asset Explorer", "Macro Trends", "Portfolio Optimizer"])
    render_credit_risk_explorer(analysis_tabs[0])
    render_news_sentiment(analysis_tabs[1])
    render_asset_explorer(analysis_tabs[2])
    render_macro_trends(analysis_tabs[3])
    render_portfolio_optimizer(analysis_tabs[4])

render_control_panel(main_tab2)
render_data_viewer(main_tab3)
