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
from static_analysis.interpreter.abstractions.sign_set import SignSet
from reader.method_signature import MethodSignature

if __name__ == "__main__":
    program = Program.load(project_root / "data" / "new")

    # Find the method to analyse
    signature = MethodSignature("org/example/App", "factorial", "int", tuple(["int"]))
    print(f"Method signature: {signature}")
    method = program.method(signature)

    # Abstract the argument(s)
    arg1 = SignSet.abstract({5})

    initial_state = AbstractState([], [arg1])
    print(f"Initial state: {initial_state}")

    interpreter = AbstractInterpreter(
        bytecode=method.bytecode,
        final=set(),
        arithmetic= SignArithmetic()
    )

    interpreter.analyse((0, initial_state))

    print(f"End states: {interpreter.final}")
