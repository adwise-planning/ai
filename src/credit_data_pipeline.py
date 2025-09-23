import pandas as pd
import numpy as np
import duckdb
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import LabelEncoder

# --- Configuration ---
DATA_DIR = "../data"
INPUT_CSV = f"{DATA_DIR}/lending_club_sample.csv"
PROCESSED_PARQUET = f"{DATA_DIR}/lending_club_processed.parquet"
DB_FILE = f"{DATA_DIR}/lending_club.duckdb"

# --- Main Functions ---

def load_and_preprocess_data(csv_path):
    """
    Loads the synthetic Lending Club data and applies preprocessing steps.
    """
    df = pd.read_csv(csv_path)
    print("Loaded raw data:")
    print(df.head())

    # 1. Label Encoding for 'loan_status'
    # We are interested in 'Fully Paid' vs 'Charged Off'
    df = df[df['loan_status'].isin(['Fully Paid', 'Charged Off'])]
    le = LabelEncoder()
    df['loan_status_encoded'] = le.fit_transform(df['loan_status'])
    print("\nAfter label encoding 'loan_status':")
    print(df[['loan_status', 'loan_status_encoded']].head())


    # 2. Feature Binning for 'annual_inc' and 'loan_amnt'
    df['income_bin'] = pd.qcut(df['annual_inc'], q=4, labels=['low', 'medium', 'high', 'very_high'])
    df['loan_amnt_bin'] = pd.qcut(df['loan_amnt'], q=4, labels=['small', 'medium', 'large', 'very_large'])
    print("\nAfter feature binning:")
    print(df[['annual_inc', 'income_bin', 'loan_amnt', 'loan_amnt_bin']].head())

    # 3. Advanced Imputation for 'annual_inc' and 'dti'
    imputer = IterativeImputer(max_iter=10, random_state=0)
    # Select only numeric columns for imputation
    numeric_cols = df.select_dtypes(include=np.number).columns
    df_numeric = df[numeric_cols]
    df[numeric_cols] = imputer.fit_transform(df_numeric)
    print("\nAfter imputation (showing info for null checks):")
    df.info()


    # 4. Temporal Cross-Validation Folds (example placeholder)
    # This would typically be used in a modeling script, but we can create the fold markers here
    df['issue_d'] = pd.to_datetime(df['issue_d'], format='%b-%Y')
    df = df.sort_values('issue_d')
    # Example: 5 folds
    df['cv_fold'] = pd.qcut(df['issue_d'].rank(method='first'), 5, labels=False)
    print("\nAfter creating temporal CV folds:")
    print(df[['issue_d', 'cv_fold']].head())

    # 5. Generate Borrower Risk Score Features
    # Credit history length in years
    df['earliest_cr_line'] = pd.to_datetime(df['earliest_cr_line'], format='%b-%Y')
    df['credit_history_length'] = (df['issue_d'] - df['earliest_cr_line']).dt.days / 365.25

    # Simple risk score (example)
    df['risk_score'] = (df['dti'] / 10) + (df['inq_last_6mths'] * 2) + (df['delinq_2yrs'] * 5)
    print("\nAfter generating risk score features:")
    print(df[['dti', 'inq_last_6mths', 'delinq_2yrs', 'credit_history_length', 'risk_score']].head())

    return df

def save_to_duckdb(df, db_file):
    """
    Saves the processed DataFrame to a DuckDB database.
    """
    con = duckdb.connect(db_file)
    con.register('processed_loans', df)
    con.execute('CREATE OR REPLACE TABLE lending_club_processed AS SELECT * FROM processed_loans')
    print(f"\nData saved to DuckDB table 'lending_club_processed' in {db_file}")
    con.close()

def save_to_parquet(df, filepath):
    """
    Saves the processed DataFrame to a Parquet file.
    """
    df.to_parquet(filepath, index=False)
    print(f"Processed data saved to {filepath}")


# --- Main Execution ---

if __name__ == "__main__":
    processed_df = load_and_preprocess_data(INPUT_CSV)

    if not processed_df.empty:
        save_to_duckdb(processed_df, DB_FILE)
        save_to_parquet(processed_df, PROCESSED_PARQUET)
        print("\n--- Sample of the final processed data ---")
        print(processed_df.head())
    else:
        print("Processing failed, no data to save.")
