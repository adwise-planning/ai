from src.data_fetcher import fetch_fred_data
import pandas as pd
import os

# --- Configuration ---
DATA_DIR = "data"
START_DATE = "2020-01-01"
END_DATE = pd.Timestamp.now().strftime("%Y-%m-%d")
CPI_SERIES = "CPIAUCNS"
OUTPUT_FILE = os.path.join(DATA_DIR, "cpi_data.parquet")

# --- Main Execution ---
if __name__ == "__main__":
    cpi_df = fetch_fred_data(CPI_SERIES, START_DATE, END_DATE)

    if not cpi_df.empty:
        cpi_df.rename(columns={CPI_SERIES: "CPI"}, inplace=True)

        # Save to parquet
        os.makedirs(DATA_DIR, exist_ok=True)
        cpi_df.to_parquet(OUTPUT_FILE)

        print(f"CPI data saved to {OUTPUT_FILE}")
        print("\n--- Sample of the CPI data ---")
        print(cpi_df.head())
    else:
        print("Failed to fetch CPI data.")
