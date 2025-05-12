#!/usr/bin/env python3
"""
Test script for the modular UI implementation
"""
import os
import sys
import time
import subprocess

def run_app():
    """Run the Streamlit app using the new modular implementation"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the new main app
    main_app_path = os.path.join(current_dir, "src", "ui", "main.py")
    
    print("=" * 50)
    print("LAUNCHING MODULAR STREAMLIT APP")
    print("=" * 50)
    print(f"App path: {main_app_path}")
    print("Starting app with improved performance...")
    
    # Run the Streamlit app
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            main_app_path, 
            "--server.headless", "true", 
            "--browser.serverAddress", "localhost",
            "--server.maxUploadSize", "100"
        ])
    except KeyboardInterrupt:
        print("\nShutting down the app...")
    except Exception as e:
        print(f"Error running the app: {e}")
        
if __name__ == "__main__":
    run_app()
