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

def main():
    parser = ArgumentParser(description="Debug tool to run a predictive test selection using specified program directories.")
    parser.add_argument("predictor", choices=["sign", "interval", "callgraph"], help="The predictor to use for the analysis.")
    parser.add_argument("--new", type=Path, help="Path to the new program directory.")
    parser.add_argument("--old", type=Path, help="Path to the old program directory.")
    
    args = parser.parse_args()

    new_program = Program.load(args.new)
    old_program = Program.load(args.old)

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
