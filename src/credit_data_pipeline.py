import pandas as pd
import numpy as np
import duckdb
import joblib
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler

# --- Configuration ---
DATA_DIR = "data"
INPUT_CSV = f"{DATA_DIR}/lending_club_sample.csv"
PROCESSED_PARQUET = f"{DATA_DIR}/lending_club_processed.parquet"
DB_FILE = f"{DATA_DIR}/lending_club.duckdb"
SCALER_FILE = f"{DATA_DIR}/scaler.joblib"

# --- Main Functions ---

import os
from datetime import datetime, timedelta

def generate_synthetic_lending_club_data(num_rows=1000):
    """
    Generates a synthetic Lending Club dataset with key features.
    """
    np.random.seed(42)
    loan_status = np.random.choice(["Fully Paid", "Charged Off", "Current"], num_rows, p=[0.7, 0.2, 0.1])
    loan_amnt = np.random.randint(1000, 35000, num_rows)
    annual_inc = np.random.uniform(30000, 150000, num_rows)
    dti = np.random.uniform(5, 40, num_rows)
    inq_last_6mths = np.random.randint(0, 5, num_rows)
    delinq_2yrs = np.random.randint(0, 3, num_rows)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)
    issue_d_timestamps = np.random.randint(start_date.timestamp(), end_date.timestamp(), num_rows)
    issue_d = [datetime.fromtimestamp(ts).strftime('%b-%Y') for ts in issue_d_timestamps]
    earliest_cr_line = []
    for ts in issue_d_timestamps:
        issue_date = datetime.fromtimestamp(ts)
        credit_history_days = np.random.randint(5*365, 20*365)
        credit_line_date = issue_date - timedelta(days=credit_history_days)
        earliest_cr_line.append(credit_line_date.strftime('%b-%Y'))
    annual_inc[np.random.choice(num_rows, int(num_rows * 0.1), replace=False)] = np.nan
    dti[np.random.choice(num_rows, int(num_rows * 0.05), replace=False)] = np.nan
    df = pd.DataFrame({
        'loan_status': loan_status, 'loan_amnt': loan_amnt, 'annual_inc': annual_inc,
        'issue_d': issue_d, 'dti': dti, 'earliest_cr_line': earliest_cr_line,
        'inq_last_6mths': inq_last_6mths, 'delinq_2yrs': delinq_2yrs,
    })
    return df

def load_and_preprocess_data(csv_path):
    """
    Loads the synthetic Lending Club data and applies preprocessing steps.
    If the source CSV does not exist, it generates it first.
    """
    if not os.path.exists(csv_path):
        print(f"Data file not found at {csv_path}. Generating synthetic data...")
        synthetic_df = generate_synthetic_lending_club_data(num_rows=2000)
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        synthetic_df.to_csv(csv_path, index=False)
        print(f"Synthetic data saved to {csv_path}")

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


    # 4. Generate Borrower Risk Score Features
    # Credit history length in years
    df['earliest_cr_line'] = pd.to_datetime(df['earliest_cr_line'], format='%b-%Y')
    df['issue_d'] = pd.to_datetime(df['issue_d'], format='%b-%Y') # Ensure issue_d is datetime
    df['credit_history_length'] = (df['issue_d'] - df['earliest_cr_line']).dt.days / 365.25

    # Simple risk score (example)
    df['risk_score'] = (df['dti'] / 10) + (df['inq_last_6mths'] * 2) + (df['delinq_2yrs'] * 5)
    print("\nAfter generating risk score features:")
    print(df[['dti', 'inq_last_6mths', 'delinq_2yrs', 'credit_history_length', 'risk_score']].head())

    # 5. Temporal Cross-Validation Folds (example placeholder)
    df = df.sort_values('issue_d')
    # Example: 5 folds
    df['cv_fold'] = pd.qcut(df['issue_d'].rank(method='first'), 5, labels=False)
    print("\nAfter creating temporal CV folds:")
    print(df[['issue_d', 'cv_fold']].head())

    # 6. Handle Outliers
    numeric_cols_for_outliers = ['loan_amnt', 'annual_inc', 'dti', 'risk_score', 'credit_history_length']
    for col in numeric_cols_for_outliers:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df[col] = np.clip(df[col], lower_bound, upper_bound)
    print("\nAfter handling outliers:")
    print(df[numeric_cols_for_outliers].describe())

    # 7. Feature Scaling
    scaler = StandardScaler()
    numeric_cols_to_scale = df.select_dtypes(include=np.number).columns.drop(['loan_status_encoded', 'cv_fold'])
    df[numeric_cols_to_scale] = scaler.fit_transform(df[numeric_cols_to_scale])
    joblib.dump(scaler, SCALER_FILE)
    print(f"\nScaler saved to {SCALER_FILE}")
    print("\nAfter feature scaling:")
    print(df[numeric_cols_to_scale].head())

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
