import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Portfolio Optimizer",
    page_icon="⚖️",
    layout="wide",
)

# --- Load Data ---
@st.cache_data
def load_portfolio_data(tickers):
    """
    Loads historical data for a list of tickers and combines them.
    """
    all_data = {}
    for ticker in tickers:
        filepath = f"data/{ticker.replace('^', '')}_historical_data.parquet"
        try:
            all_data[ticker] = pd.read_parquet(filepath)['Close']
        except FileNotFoundError:
            st.error(f"Data for {ticker} not found. Please run the yahoo_finance_pipeline.py first.")
            return None

    return pd.concat(all_data, axis=1).dropna()

tickers = ["AAPL", "^GSPC"]
portfolio_df = load_portfolio_data(tickers)


# --- Main Dashboard ---
st.title("⚖️ Portfolio Optimizer")

if portfolio_df is not None:
    st.markdown("""
    This tool helps you visualize the risk-return trade-off for a portfolio of assets.
    The efficient frontier represents the set of optimal portfolios.
    """)

    # --- Calculate Returns and Covariance ---
    returns = portfolio_df.pct_change().dropna()
    mean_returns = returns.mean() * 252  # Annualized
    cov_matrix = returns.cov() * 252  # Annualized

    # --- Sidebar for User Input ---
    st.sidebar.header("Your Portfolio Weights")
    w_aapl = st.sidebar.slider("Apple (AAPL) Weight", 0.0, 1.0, 0.5, 0.05)
    w_gspc = 1 - w_aapl
    st.sidebar.write(f"S&P 500 (^GSPC) Weight: {w_gspc:.2f}")

    # --- Calculate User's Portfolio Metrics ---
    user_weights = np.array([w_aapl, w_gspc])
    user_return = np.sum(mean_returns * user_weights)
    user_volatility = np.sqrt(np.dot(user_weights.T, np.dot(cov_matrix, user_weights)))
    user_sharpe = user_return / user_volatility

    st.header("Your Portfolio")
    col1, col2, col3 = st.columns(3)
    col1.metric("Expected Annual Return", f"{user_return:.2%}")
    col2.metric("Annual Volatility (Risk)", f"{user_volatility:.2%}")
    col3.metric("Sharpe Ratio", f"{user_sharpe:.2f}")


    # --- Calculate and Plot Efficient Frontier ---
    st.header("Efficient Frontier")

    num_portfolios = 5000
    results = np.zeros((3, num_portfolios))
    all_weights = np.zeros((num_portfolios, len(tickers)))

    for i in range(num_portfolios):
        weights = np.random.random(len(tickers))
        weights /= np.sum(weights)

        all_weights[i,:] = weights

        portfolio_return = np.sum(mean_returns * weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        results[0,i] = portfolio_return
        results[1,i] = portfolio_volatility
        results[2,i] = portfolio_return / portfolio_volatility


    # --- Create Chart ---
    fig = go.Figure()

    # Scatter plot for the efficient frontier
    fig.add_trace(go.Scatter(
        x=results[1,:],
        y=results[0,:],
        mode='markers',
        marker=dict(
            color=results[2,:], # Color by Sharpe Ratio
            showscale=True,
            colorscale='Viridis',
            size=5,
            colorbar=dict(title='Sharpe Ratio')
        ),
        name='Portfolios'
    ))

    # Highlight the user's portfolio
    fig.add_trace(go.Scatter(
        x=[user_volatility],
        y=[user_return],
        mode='markers',
        marker=dict(color='red', size=12, symbol='star'),
        name='Your Portfolio'
    ))

    # Highlight the max Sharpe ratio portfolio
    max_sharpe_idx = np.argmax(results[2])
    max_sharpe_return = results[0,max_sharpe_idx]
    max_sharpe_volatility = results[1,max_sharpe_idx]
    fig.add_trace(go.Scatter(
        x=[max_sharpe_volatility],
        y=[max_sharpe_return],
        mode='markers',
        marker=dict(color='green', size=12, symbol='diamond'),
        name='Max Sharpe Ratio'
    ))


    fig.update_layout(
        title='Efficient Frontier',
        xaxis_title='Volatility (Risk)',
        yaxis_title='Expected Return',
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)


else:
    st.warning("Could not load data to display the dashboard.")
