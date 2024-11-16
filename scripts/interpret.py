#!/usr/bin/env python3

from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from reader.program import Program
from static_analysis.interpreter.abstract_interpreter import AbstractInterpreter
from static_analysis.interpreter.abstractions.abstract_state import AbstractState
from static_analysis.interpreter.arithmetic.sign_arithmetic import SignArithmetic

def main():
    program = Program.load(project_root / "data" / "new")
    
    for _, method in program.all_test_methods():
        if method.signature.name == "<init>":
            continue

        print(f"Running test: {method.signature}")

        initial_state = AbstractState([], [])

        interpreter = AbstractInterpreter(
            bytecode=method.bytecode,
            arithmetic= SignArithmetic()
        )

        interpreter.analyse((0, initial_state))

        print(f"End states: {interpreter.final}")
        print(f"PCs run: {interpreter.pcs}")


if __name__ == "__main__":
    main()