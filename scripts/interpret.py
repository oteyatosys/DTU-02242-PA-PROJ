#!/usr/bin/env python3

from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from reader import Program, MethodSignature
from static_analysis.interpreter.abstract_interpreter import AbstractInterpreter
from static_analysis.interpreter.abstract_sign_interpreter import PC, AbstractSignInterpreter
from static_analysis.interpreter.abstract_interval_interpreter import AbstractIntervalInterpreter
from static_analysis.interpreter.abstractions.abstract_state import AbstractState
from static_analysis.interpreter.abstractions.interval import Interval

import logging as l

l.basicConfig(level=l.DEBUG)

def run_without_parameters(interpreter: AbstractInterpreter, signature: MethodSignature):
    pc = PC(signature, 0)
    initial_state = AbstractState([], {})

    touched = interpreter.analyse(pc, initial_state)

    print(f"Running {signature}")
    print("=================================")

    for sig, offsets in touched.items():
        print(sig)
        print("  ", ", ".join(map(str, offsets)))
    print()

def run_all_tests():
    program = Program.load(project_root / "data" / "new")

    interpreter = AbstractIntervalInterpreter(program)
    # interpreter = AbstractSignInterpreter(program)

    for _, method in program.all_test_methods():
        run_without_parameters(interpreter, method.signature)

def run_one_test(signature_str : str):
    program = Program.load(project_root / "data" / "new")
    interpreter = AbstractIntervalInterpreter(program)
    signature = MethodSignature.from_str(signature_str)
    run_without_parameters(interpreter, signature)

def main():
    run_all_tests()
    # run_one_test("org/example/MathTest.testIsPrime17:()V")

if __name__ == "__main__":
    main()
