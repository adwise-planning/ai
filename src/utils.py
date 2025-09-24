import subprocess
import os

def run_script(script_path):
    """
    Runs a Python script as a subprocess and captures its output.
    """
    if not os.path.exists(script_path):
        return f"Error: Script not found at {script_path}"

    try:
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running {script_path}:\n{e.stderr}"
