#!/usr/bin/env python3

from pathlib import Path
import sys

from prediction.abstract_predictor import AbstractPredictor
from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from typing import Set
from reader.method_signature import MethodSignature
from reader.program import Program
from syntactic_analysis.bytecode.call_graph import build_call_graph

data_dir: Path = project_root / "data"

new_dir = data_dir / "new"
old_dir = data_dir / "old"

def main():
    new_program = Program.load(new_dir)
    old_program = Program.load(old_dir)

    predictor: TestPredictor = AbstractPredictor()

    test: Set[MethodSignature] = predictor.predict(old_program, new_program)

    print("Predicted test methods:")
    print(test)

    # ints = get_int_literals(program)

    # print("Int literals found in the program:")
    # print(ints)

if __name__ == "__main__":
    main()