import streamlit as st
import pandas as pd
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Data Viewer",
    page_icon="📄",
    layout="wide",
)

# --- Main Dashboard ---
st.title("📄 Data Viewer")
st.markdown("Select a dataset from the `/data` directory to view its contents.")

# --- Data Selection ---
DATA_DIR = "data"
try:
    available_files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
except FileNotFoundError:
    available_files = []

if not available_files:
    st.warning(f"No data files found in the `{DATA_DIR}` directory. Please run the data pipelines first.")
else:
    selected_file = st.selectbox("Select a data file", options=available_files)

    if selected_file:
        filepath = os.path.join(DATA_DIR, selected_file)
        st.subheader(f"Preview of `{selected_file}`")

        try:
            # Load the data based on file extension
            if selected_file.endswith('.parquet'):
                df = pd.read_parquet(filepath)
            elif selected_file.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif selected_file.endswith('.gz'):
                 df = pd.read_csv(filepath, compression='gzip')
            else:
                st.error("Unsupported file format. Please select a Parquet or CSV file.")
                df = None

            if df is not None:
                st.dataframe(df)

                # Show some basic info
                st.subheader("Data Information")
                st.write(f"**Shape:** {df.shape[0]} rows, {df.shape[1]} columns")

        except Exception as e:
            st.error(f"Error loading data file: {e}")
