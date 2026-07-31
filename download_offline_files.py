#!/usr/bin/env python3
"""
Download offline static files for Chore Assistant
Grabs Bootstrap, Font Awesome, Chart.js, and dependencies
"""

import os
import urllib.request
from pathlib import Path

# Define the files to download
FILES_TO_DOWNLOAD = [
    # Bootstrap CSS
    {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
        "path": "static/css/bootstrap.min.css"
    },
    # Bootstrap JS
    {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js",
        "path": "static/js/bootstrap.bundle.min.js"
    },
    # Font Awesome CSS
    {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        "path": "static/css/font-awesome.min.css"
    },
    # Font Awesome webfonts (multiple files needed)
    {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2",
        "path": "static/fonts/fa-solid-900.woff2"
    },
    {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2",
        "path": "static/fonts/fa-brands-400.woff2"
    },
    # Chart.js
    {
        "url": "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",
        "path": "static/js/chart.umd.min.js"
    },
    # Chart.js DataLabels plugin
    {
        "url": "https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js",
        "path": "static/js/chartjs-plugin-datalabels.min.js"
    }
]

def create_directories():
    """Create necessary static directories"""
    dirs = ["static/css", "static/js", "static/fonts"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ready: {dir_path}")

def download_files():
    """Download all required files"""
    print("\n📥 Starting downloads...\n")
    
    for file_info in FILES_TO_DOWNLOAD:
        url = file_info["url"]
        path = file_info["path"]
        
        try:
            print(f"Downloading: {path}")
            urllib.request.urlretrieve(url, path)
            print(f"  ✓ Saved to {path}\n")
        except Exception as e:
            print(f"  ✗ ERROR downloading {path}: {e}\n")
            return False
    
    return True

def main():
    print("=" * 60)
    print("Chore Assistant - Offline Files Downloader")
    print("=" * 60)
    
    # Create directories
    create_directories()
    
    # Download files
    success = download_files()
    
    if success:
        print("=" * 60)
        print("✅ All files downloaded successfully!")
        print("=" * 60)
        print("\nNext step: Run 'python3 app.py' to test offline mode")
        return 0
    else:
        print("=" * 60)
        print("❌ Download failed. Check your internet connection.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit(main())