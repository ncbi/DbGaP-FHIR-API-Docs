"""Make the adjacent notebook helpers importable when testing from any directory."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
