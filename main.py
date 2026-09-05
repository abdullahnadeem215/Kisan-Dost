"""
Kisan Dost Main CLI Entry Point.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.presentation.terminal import main

if __name__ == "__main__":
    main()
