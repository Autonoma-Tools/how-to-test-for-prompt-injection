"""Make the repository root importable so `from src import ...` works anywhere.

Keeps `pytest`, `pytest tests/`, and `pytest tests/test_red_team.py` all
behaving the same way, with no editable install step.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
