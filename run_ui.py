"""
Launcher script for the Streamlit-based YouTube Smart Agent UI.
"""
import streamlit as st
import subprocess
import os
import sys

if __name__ == "__main__":
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Streamlit app
    streamlit_app_path = os.path.join(current_dir, "src", "ui", "streamlit_app.py")
    
    print(f"Launching YouTube Smart Agent UI...")
    print(f"You can access the UI in your browser after it starts.")
    
    # Run Streamlit app
    subprocess.run([sys.executable, "-m", "streamlit", "run", streamlit_app_path, "--server.headless", "true", "--browser.serverAddress", "localhost"])