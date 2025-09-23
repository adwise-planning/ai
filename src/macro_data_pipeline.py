import pandas_datareader.data as web
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
    print(f"Fetching CPI data from FRED ({CPI_SERIES})...")
    try:
        cpi_df = web.DataReader(CPI_SERIES, "fred", START_DATE, END_DATE)
        cpi_df.rename(columns={CPI_SERIES: "CPI"}, inplace=True)

        print(f"Successfully fetched {len(cpi_df)} rows of CPI data.")

        # Save to parquet
        os.makedirs(DATA_DIR, exist_ok=True)
        cpi_df.to_parquet(OUTPUT_FILE)

        print(f"CPI data saved to {OUTPUT_FILE}")
        print("\n--- Sample of the CPI data ---")
        print(cpi_df.head())

    except Exception as e:
        print(f"Error fetching data from FRED: {e}")
