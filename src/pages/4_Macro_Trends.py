import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Page Configuration ---
st.set_page_config(
    page_title="Macro Trends",
    page_icon="🌍",
    layout="wide",
)

# --- Load Data ---
@st.cache_data
def load_data():
    """
    Loads CPI and S&P 500 data.
    """
    try:
        cpi_df = pd.read_parquet("data/cpi_data.parquet")
        gspc_df = pd.read_parquet("data/GSPC_historical_data.parquet")
        return cpi_df, gspc_df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Please run the required data pipelines first.")
        return None, None

cpi_df, gspc_df = load_data()


# --- Main Dashboard ---
st.title("🌍 Macro Trends: CPI vs. S&P 500")

if cpi_df is not None and gspc_df is not None:
    st.markdown("""
    This page analyzes the relationship between inflation (CPI) and the stock market (S&P 500).
    """)

    # --- Preprocess Data ---
    # Resample S&P 500 data to monthly
    gspc_monthly = gspc_df['Close'].resample('M').last()

    # Calculate monthly returns for S&P 500
    gspc_returns = gspc_monthly.pct_change() * 100

    # Calculate year-over-year percentage change for CPI
    cpi_pct_change = cpi_df['CPI'].pct_change(12) * 100

    # Combine into a single DataFrame
    combined_df = pd.DataFrame({
        'S&P 500 Returns': gspc_returns,
        'CPI % Change': cpi_pct_change
    }).dropna()


    # --- Create Charts ---
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("S&P 500 Monthly Returns vs. CPI Year-over-Year Change", "12-Month Rolling Correlation")
    )

    # 1. Returns vs. CPI Chart
    fig.add_trace(go.Scatter(x=combined_df.index, y=combined_df['S&P 500 Returns'], name='S&P 500 Returns', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=combined_df.index, y=combined_df['CPI % Change'], name='CPI % Change', line=dict(color='red')), row=1, col=1)


    # 2. Rolling Correlation Chart
    rolling_corr = combined_df['S&P 500 Returns'].rolling(window=12).corr(combined_df['CPI % Change'])
    fig.add_trace(go.Scatter(x=rolling_corr.index, y=rolling_corr, name='Rolling Correlation', line=dict(color='purple')), row=2, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="grey", row=2, col=1)


    # --- Update Layout ---
    fig.update_layout(
        height=700,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)


    # --- Raw Data ---
    st.header("Combined Data")
    st.dataframe(combined_df)

else:
    st.warning("Could not load data to display the dashboard.")
