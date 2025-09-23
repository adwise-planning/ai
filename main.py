import argparse
import subprocess
import os

# --- Script Definitions ---
PIPELINE_SCRIPTS = [
    "src/credit_data_pipeline.py",
    "src/yahoo_finance_pipeline.py",
    "src/binance_historical_pipeline.py",
    "src/macro_data_pipeline.py",
    "src/news_pipeline.py",
]

DASHBOARD_SCRIPT = "dashboard.py"


# --- Functions ---

def run_pipelines():
    """
    Runs all the data pipeline scripts in order.
    """
    print("--- Running all data pipelines ---")
    for script in PIPELINE_SCRIPTS:
        print(f"\n>>> Running {script}...")
        try:
            # We need to handle the case where a file might not exist
            if not os.path.exists(script):
                print(f"!!! WARNING: Script not found, skipping: {script}")
                continue
            subprocess.run(["python", script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"!!! ERROR: Failed to run {script}. Aborting. !!!")
            print(e)
            break
        except FileNotFoundError:
            print(f"!!! WARNING: Script not found, skipping: {script}")

    print("\n--- All data pipelines finished ---")


def run_dashboard():
    """
    Launches the Streamlit dashboard.
    """
    print("--- Launching Streamlit dashboard ---")
    print(f">>> Running: streamlit run {DASHBOARD_SCRIPT}")
    try:
        subprocess.run(["streamlit", "run", DASHBOARD_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"!!! ERROR: Failed to launch dashboard. !!!")
        print(e)
    except FileNotFoundError:
        print("!!! ERROR: 'streamlit' command not found. Make sure Streamlit is installed. !!!")


# --- Main Execution ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Main entry point for the Financial Analysis Dashboard project.")
    parser.add_argument(
        "--run-pipelines",
        action="store_true",
        help="Run all data pipelines to fetch and process data."
    )
    parser.add_argument(
        "--run-dashboard",
        action="store_true",
        help="Launch the Streamlit dashboard."
    )

    args = parser.parse_args()

    if args.run_pipelines:
        run_pipelines()

    if args.run_dashboard:
        run_dashboard()

    if not args.run_pipelines and not args.run_dashboard:
        print("No action specified. Use --run-pipelines or --run-dashboard.")
        parser.print_help()
