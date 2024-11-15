#!/usr/bin/env python3

from pathlib import Path
import sys

from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from typing import Set
from reader.method_signature import MethodSignature
from reader.program import Program
from syntactic_analysis.bytecode.call_graph import build_call_graph
import jsondiff


data_dir: Path = project_root / "data"

new_dir = data_dir / "new"
old_dir = data_dir / "old"

if __name__ == "__main__":
    new_program = Program.load(new_dir)
    old_program = Program.load(old_dir)

    predictor: TestPredictor = CallGraphPredictor(old_program, new_program)

    test: Set[MethodSignature] = predictor.predict()

    # ints = get_int_literals(program)

    # print("Int literals found in the program:")
    # print(ints)
