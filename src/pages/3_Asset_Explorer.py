import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Page Configuration ---
st.set_page_config(
    page_title="Asset Explorer",
    page_icon="📈",
    layout="wide",
)

# --- Load Data ---
@st.cache_data
def load_asset_data(ticker):
    """
    Loads the historical data for a given asset.
    """
    filepath = f"data/{ticker}_historical_data.parquet"
    try:
        df = pd.read_parquet(filepath)
        return df
    except FileNotFoundError:
        st.error(f"Data for {ticker} not found. Please run the corresponding data pipeline first.")
        return None

# For now, we will hardcode the asset to AAPL
# A future improvement would be to have a dropdown to select from available assets
ticker = "AAPL"
df = load_asset_data(ticker)


# --- Main Dashboard ---
st.title(f"📈 Asset Explorer: {ticker}")

if df is not None:
    st.markdown(f"Displaying historical data and technical indicators for **{ticker}**.")

    # --- Create Charts ---
    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f"{ticker} Price (OHLC)", "Volume", "RSI", "MACD"),
        row_heights=[0.6, 0.1, 0.15, 0.15]
    )

    # 1. Price Chart (OHLC) with Bollinger Bands
    fig.add_trace(go.Candlestick(x=df.index,
                                open=df['Open'],
                                high=df['High'],
                                low=df['Low'],
                                close=df['Close'],
                                name='OHLC'),
                  row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['BBU_5_2.0_2.0'], name='Upper BB', line=dict(color='blue', width=1, dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BBM_5_2.0_2.0'], name='Middle BB', line=dict(color='blue', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BBL_5_2.0_2.0'], name='Lower BB', line=dict(color='blue', width=1, dash='dash')), row=1, col=1)


    # 2. Volume Chart
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'), row=2, col=1)

    # 3. RSI Chart
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI_14'], name='RSI'), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)


    # 4. MACD Chart
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'], name='MACD', line=dict(color='blue')), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], name='Signal', line=dict(color='orange')), row=4, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['MACDh_12_26_9'], name='Histogram', marker_color='grey'), row=4, col=1)


    # --- Update Layout ---
    fig.update_layout(
        height=800,
        showlegend=False,
        xaxis_rangeslider_visible=False,
    )
    fig.update_xaxes(showticklabels=True, row=1, col=1)
    fig.update_xaxes(showticklabels=True, row=2, col=1)
    fig.update_xaxes(showticklabels=True, row=3, col=1)
    fig.update_xaxes(showticklabels=True, row=4, col=1)


    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Could not load data to display the dashboard.")
