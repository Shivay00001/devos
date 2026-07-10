#!/usr/bin/env python3
import sys
import os

# Add the current directory to PYTHONPATH so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_engine.core.processor import main

if __name__ == "__main__":
    main()
