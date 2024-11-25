#!/usr/bin/env python3

from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from reader import Program, MethodSignature
from static_analysis.interpreter.abstract_interpreter import PC, AbstractInterpreter
from static_analysis.interpreter.it_abstract_interpreter import ItAbstractInterpreter
from static_analysis.interpreter.abstractions.abstract_state import AbstractState
from static_analysis.interpreter.arithmetic.sign_arithmetic import SignArithmetic
from static_analysis.interpreter.arithmetic.interval_arithmetic import IntervalArithmetic
from syntactic_analysis.scanner import get_int_literals

import logging as l

l.basicConfig(level=l.DEBUG)

def main():
    program = Program.load(project_root / "data" / "new")
    signature = MethodSignature.from_str("org.example.FunsTest.testZero:()V")
    interesting_values = get_int_literals(program)
    
    interpreter = AbstractInterpreter(
        program=program
    )

    pc = PC(signature, 0)
    initial_state = AbstractState([], {})

    touched = interpreter.analyse(pc, initial_state)

    print(f"End states: {interpreter.final}")
    print(f"Touched: {touched}")

if __name__ == "__main__":
    main()
