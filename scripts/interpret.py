#!/usr/bin/env python3

from pathlib import Path
from argparse import ArgumentParser
from reader import Program, MethodSignature
from static_analysis.interpreter.abstract_interpreter import AbstractInterpreter
from static_analysis.interpreter.abstract_sign_interpreter import PC, AbstractSignInterpreter
from static_analysis.interpreter.abstract_interval_interpreter import AbstractIntervalInterpreter
from static_analysis.interpreter.abstractions.abstract_state import AbstractState
from preparation.prepare import perform_data_rotation

import logging as l

project_root = Path(__file__).parent.parent

def run_without_parameters(interpreter: AbstractInterpreter, signature: MethodSignature):
    pc = PC(signature, 0)
    initial_state = AbstractState([], {})

    print(f"\nRunning {signature}")
    print("=================================")
    touched = interpreter.analyse(pc, initial_state)
    for sig, offsets in touched.items():
        print(sig)
        print("  ", ", ".join(map(str, offsets)))
    print()

def main():
    parser = ArgumentParser(description="Run the interpreter on all test methods.")
    parser.add_argument("interpreter", choices=["sign", "interval"], help="The interpreter to use.")
    parser.add_argument("--skip-rotation", action="store_true", help="Skip data rotation.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    parser.add_argument("--select", help="Select only methods where the name contains this string.", default="")

    args = parser.parse_args()

    # Enable debug logging
    if args.verbose:
        l.basicConfig(level=l.DEBUG)

    # Perform data rotation
    if not args.skip_rotation:
        l.debug("Performing data rotation")
        perform_data_rotation(
            project_root / "java-example",
            project_root / "data"
        )

    # Load the interpreter with the program
    program = Program.load(project_root / "data" / "new")
    if args.interpreter == "sign":
        interpreter = AbstractSignInterpreter(program)
    elif args.interpreter == "interval":
        interpreter = AbstractIntervalInterpreter(program)

    # Run the interpreter on all, or specific, test methods
    for _, method in program.all_test_methods():
        if args.select not in method.signature.name:
            continue
        run_without_parameters(interpreter, method.signature)

if __name__ == "__main__":
    main()
