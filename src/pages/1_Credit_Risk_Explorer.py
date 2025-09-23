import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Credit Risk Explorer",
    page_icon="💳",
    layout="wide",
)

import os

# --- Load Data ---
@st.cache_data
def load_data():
    """
    Loads the processed Lending Club data.
    """
    # Construct a robust path to the data file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    data_file = os.path.join(project_root, "data", "lending_club_processed.parquet")

    try:
        df = pd.read_parquet(data_file)
        return df
    except FileNotFoundError:
        st.error("Processed data file not found. Please run 'python src/credit_data_pipeline.py' first.")
        return None

df = load_data()

# --- Main Dashboard ---
st.title("💳 Credit Risk Explorer")

if df is not None:
    st.markdown("""
    This page allows you to explore the Lending Club dataset.
    Use the filters on the left to analyze different segments of borrowers.
    """)

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    loan_status_filter = st.sidebar.multiselect(
        "Loan Status",
        options=df["loan_status"].unique(),
        default=df["loan_status"].unique(),
    )

    income_bin_filter = st.sidebar.multiselect(
        "Income Bin",
        options=df["income_bin"].unique(),
        default=df["income_bin"].unique(),
    )

    loan_amnt_slider = st.sidebar.slider(
        "Loan Amount",
        min_value=int(df["loan_amnt"].min()),
        max_value=int(df["loan_amnt"].max()),
        value=(int(df["loan_amnt"].min()), int(df["loan_amnt"].max())),
    )

    # --- Filter Data ---
    filtered_df = df[
        (df["loan_status"].isin(loan_status_filter)) &
        (df["income_bin"].isin(income_bin_filter)) &
        (df["loan_amnt"] >= loan_amnt_slider[0]) &
        (df["loan_amnt"] <= loan_amnt_slider[1])
    ]

    # --- Display Metrics ---
    st.header("Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Loans", f"{len(filtered_df):,}")
    col2.metric("Average Loan Amount", f"${filtered_df['loan_amnt'].mean():,.2f}")
    col3.metric("Average DTI", f"{filtered_df['dti'].mean():.2f}")


    # --- Display Charts ---
    st.header("Visualizations")

    # Loan Status Distribution
    fig_loan_status = px.pie(
        filtered_df,
        names="loan_status",
        title="Loan Status Distribution",
        hole=0.3,
    )
    st.plotly_chart(fig_loan_status, use_container_width=True)

    # Loan Amount by Income
    fig_loan_by_income = px.box(
        filtered_df,
        x="income_bin",
        y="loan_amnt",
        color="loan_status",
        title="Loan Amount by Income Bin",
    )
    st.plotly_chart(fig_loan_by_income, use_container_width=True)

    # DTI vs. Risk Score
    fig_dti_risk = px.scatter(
        filtered_df,
        x="dti",
        y="risk_score",
        color="loan_status",
        title="Debt-to-Income (DTI) vs. Risk Score",
        hover_data=['loan_amnt', 'annual_inc']
    )
    st.plotly_chart(fig_dti_risk, use_container_width=True)


    # --- Raw Data ---
    st.header("Raw Data")
    st.dataframe(filtered_df)

else:
    st.warning("Could not load data to display the dashboard.")
