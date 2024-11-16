#!/usr/bin/env python3

from pathlib import Path
from preparation.prepare import perform_rotation

def main():
    perform_rotation(
        Path("java-example")
    )

if __name__ == "__main__":
    main()