import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Control Panel",
    page_icon="🛠️",
    layout="wide",
)

# --- Main Dashboard ---
st.title("🛠️ Control Panel")

st.markdown("""
This page provides administrative tools to run data pipelines and manage the application's configuration.
""")

# --- Pipeline Execution ---
st.header("Pipeline Execution")
st.markdown("Run data pipelines to fetch and process the latest data.")

from src.utils import run_script
import time

PIPELINE_SCRIPTS = [
    "src/financial_data_pipeline.py",
    "src/credit_data_pipeline.py",
    "src/macro_data_pipeline.py",
    "src/news_pipeline.py",
]

if 'pipeline_output' not in st.session_state:
    st.session_state.pipeline_output = ""

if st.button("Run All Pipelines"):
    st.session_state.pipeline_output = ""
    with st.spinner("Running all pipelines... This may take a few minutes."):
        full_output = ""
        for script in PIPELINE_SCRIPTS:
            full_output += f">>> Running {script}...\n"
            st.session_state.pipeline_output = full_output
            time.sleep(0.1) # Give the UI a moment to update

            output = run_script(script)
            full_output += output + "\n\n"
            st.session_state.pipeline_output = full_output
            time.sleep(0.1)

    st.success("All pipelines finished.")

st.subheader("Individual Pipelines")
cols = st.columns(len(PIPELINE_SCRIPTS))

for i, script in enumerate(PIPELINE_SCRIPTS):
    with cols[i]:
        if st.button(script.split('/')[-1]):
            st.session_state.pipeline_output = f">>> Running {script}...\n"
            with st.spinner(f"Running {script}..."):
                output = run_script(script)
                st.session_state.pipeline_output += output
            st.success(f"Finished running {script}.")

st.code(st.session_state.pipeline_output, language='bash')


# --- Configuration Management ---
st.header("Configuration Management")
st.markdown("View and edit the `config.ini` file for the application.")

import os

CONFIG_FILE = 'config.ini'

try:
    with open(CONFIG_FILE, 'r') as f:
        config_text = f.read()
except FileNotFoundError:
    st.error(f"Configuration file not found at {CONFIG_FILE}")
    config_text = ""

new_config_text = st.text_area("config.ini", value=config_text, height=300)

if st.button("Save Configuration"):
    try:
        with open(CONFIG_FILE, 'w') as f:
            f.write(new_config_text)
        st.success(f"Successfully saved configuration to {CONFIG_FILE}")
        st.rerun() # Rerun to reflect changes
    except Exception as e:
        st.error(f"Failed to save configuration: {e}")
