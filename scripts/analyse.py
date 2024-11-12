#!/usr/bin/env python3

from pathlib import Path
import sys
import subprocess

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from reader.program import Program
from syntactic_analysis.scanner import get_int_literals

def prepare_data():
    subprocess.run([str(project_root / "prepare_data.sh")])

if __name__ == "__main__":
    program = Program.load(project_root / "data" / "new")

    print("All methods in the program:")
    print(program.all_methods())
    for file, method in program.all_methods():
        print("method")
        print(file.name)
        print(method.name)
        print(method.signature)

    # ints = get_int_literals(program)

    # print("Int literals found in the program:")
    # print(ints)
