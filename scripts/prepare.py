#!/usr/bin/env python3

from pathlib import Path
import sys
import subprocess

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

if __name__ == "__main__":
    subprocess.run([str(project_root / "prepare_data.sh")])
