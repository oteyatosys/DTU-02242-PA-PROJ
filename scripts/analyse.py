#!/usr/bin/env python3

from pathlib import Path
from argparse import ArgumentParser
from prediction.abstract_interval_predictor import AbstractIntervalPredictor
from prediction.abstract_sign_predictor import AbstractSignPredictor
from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor
from typing import Set
from reader.method_signature import MethodSignature
from reader.program import Program

project_root = Path(__file__).parent.parent
data_dir: Path = project_root / "data"

new_dir = data_dir / "new"
old_dir = data_dir / "old"

def main():
    parser = ArgumentParser(description="Debug tool to run a predictive test selection on the programs in the data directory.")
    parser.add_argument("predictor", choices=["sign", "interval", "callgraph"], help="The predictor to use for the analysis.")
    
    args = parser.parse_args()

    new_program = Program.load(new_dir)
    old_program = Program.load(old_dir)

    if args.predictor == "sign":
        predictor: TestPredictor = AbstractSignPredictor()
    elif args.predictor == "interval":
        predictor: TestPredictor = AbstractIntervalPredictor()
    elif args.predictor == "callgraph":
        predictor: TestPredictor = CallGraphPredictor()

    test: Set[MethodSignature] = predictor.predict(old_program, new_program)

    print("Predicted test methods:")
    print(test)

if __name__ == "__main__":
    main()
