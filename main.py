#!/usr/bin/env python3
"""
MP3 Album Merger
Main entry point for the application
"""

import sys
from src.gui import MP3AlbumMergerApp

def main():
    app = MP3AlbumMergerApp()
    app.run()

if __name__ == "__main__":
    main()
