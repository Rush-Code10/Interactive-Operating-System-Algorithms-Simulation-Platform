#!/usr/bin/env python3
"""
Simple launcher for the OS Algorithms Simulator Tkinter App
"""

import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tkinter_simulator import main
    print("Starting OS Algorithms Simulator...")
    main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install matplotlib")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)