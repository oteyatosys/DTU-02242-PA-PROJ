#!/usr/bin/env python3

from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from reader.program import Program
from static_analysis.interpreter.abstract_interpreter import PC, AbstractInterpreter
from static_analysis.interpreter.abstractions.abstract_state import AbstractState
from static_analysis.interpreter.arithmetic.sign_arithmetic import SignArithmetic
import logging as l

# l.basicConfig(level=l.DEBUG)

def main():
    program = Program.load(project_root / "data" / "new")
    
    for _, method in program.all_test_methods():
        print("-------------------------")
        print(f"Running test: {method.signature}")

        # if method.name != "testGetInt":
        #     print("Skipping")
        #     continue

        interpreter = AbstractInterpreter(
            program=program,
            arithmetic= SignArithmetic()
        )

        pc = PC(method.signature, 0)
        initial_state = AbstractState([], [])

        touched = interpreter.analyse(pc, initial_state)

        print(f"End states: {interpreter.final}")
        print(f"Touched: {touched}")


if __name__ == "__main__":
    main()
