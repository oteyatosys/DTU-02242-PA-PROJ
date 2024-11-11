#!/usr/bin/env python3

from pathlib import Path
import sys
import subprocess

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from reader.program import Program
from syntactic_analysis.scanner import get_int_literals

def load_program() -> Program:
    bytecode_dir = project_root / "data" / "bytecode"
    source_dir = project_root / "data" / "source"
    test_source_dir = project_root / "data" / "test_source"
    test_bytecode_dir = project_root / "data" / "test_bytecode"

    return Program() \
        .scan(source_dir, bytecode_dir) \
        .scan_tests(test_source_dir, test_bytecode_dir)

def prepare_data():
    subprocess.run([str(project_root / "prepare_data.sh")])

if __name__ == "__main__":
    prepare_data()


    # program = load_program()

    # ints = get_int_literals(program)

    # print("Int literals found in the program:")
    # print(ints)
