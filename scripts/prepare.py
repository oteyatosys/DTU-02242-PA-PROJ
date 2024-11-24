#!/usr/bin/env python3

from pathlib import Path
from preparation.prepare import perform_data_rotation

project_root = Path(__file__).parent.parent

def main():
    perform_data_rotation(
        Path("java-example"),
        Path("data")
    )

if __name__ == "__main__":
    main()