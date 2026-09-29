#!/usr/bin/env python3
"""
Entry point for running omni-agents with `python -m omni_agents`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure parent directory (src/) is in sys.path when executed directly as a script
_SRC_DIR = Path(__file__).resolve().parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from omni_agents.cli import main

if __name__ == "__main__":
    sys.exit(main())
