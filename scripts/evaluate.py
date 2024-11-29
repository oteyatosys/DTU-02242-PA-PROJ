from argparse import ArgumentParser
from pathlib import Path
from evaluation.evaluator import Evaluator
from evaluation.results import TestSuiteResult
from evaluation import TestSuiteBuilder
from prediction.abstract_sign_predictor import AbstractSignPredictor
from prediction.abstract_interval_predictor import AbstractIntervalPredictor
from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor
from evaluation.test_scenario_builder import TestSuiteBuilder
import pickle

project_root = Path(__file__).parent.parent

def main():
    parser = ArgumentParser(description="Run test suite evaluation with specified predictor.")
    parser.add_argument("predictor", choices=["sign", "interval", "callgraph"], help="The predictor to use for the evaluation.")
    parser.add_argument("--no-threads", action="store_true", help="Disable threading for the evaluation.")
    args = parser.parse_args()
    
    evaluator = Evaluator(0 if args.no_threads else None)

    if args.predictor == "sign":
        predictor: TestPredictor = AbstractSignPredictor()
    elif args.predictor == "interval":
        predictor: TestPredictor = AbstractIntervalPredictor()
    elif args.predictor == "callgraph":
        predictor: TestPredictor = CallGraphPredictor()

    builder = TestSuiteBuilder(project_root / "java-example")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Funs.java", "int zero()")
            sb.move(2)
            sb.replace("return 42;")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Funs.java", "int one()")
            sb.move(2)
            sb.replace("return 42;")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Funs.java", "int two()")
            sb.move(2)
            sb.replace("return 42;")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Math.java", "int negate(int n)")
            # Make abs throw assertion error for all cases
            sb.add("assert false;")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Math.java", "int abs(int n)")
            # Make abs throw assertion error for all cases
            sb.add("assert false;")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Math.java", "int gcd(int a, int b)")
            sb.move(3)
            # Make wrong return value for gcd where b != 0
            sb.add("b += 1;")

            # Calling gcd(5, 0) where b is 0, should result in a skipped while loop,
            # and thereby skipping testGcdWithZero, this is not the case.
            # In both Sign and Interval abstractions, we are able to specify zero, 
            # and abs(0) should still return zero, but due to the preceding call to abs(5)
            # the state for the PC is already containing a {"+"} or a [5, 5]

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Math.java", "int lcm(int a, int b)")
            # Make lcm throw assertion error for all cases
            sb.add("assert false;")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Math.java", "int factorial(int n)")
            sb.move(1)
            # Make wrong return value for factorial where n > 0
            sb.replace("return n == 0 ? 1 : n * factorial(n - 1) + 6;")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Math.java", "int fibonacci(int n)")
            sb.move(1)
            # Make abs throw assertion error for cases where n > 2
            sb.add("assert false;")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Math.java", "boolean dividesBy(int a, int b)")
            sb.add("assert false;")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Math.java", "boolean isPrime(int n)")
            sb.move(4)
            # Make isPrime throw assertion error if no divisor is found
            sb.add("assert false;")

    test_suite = builder.build()

    result: TestSuiteResult = evaluator.evaluate_suite(predictor, test_suite)

    result.print_stats()

    with open("result.pkl", "wb") as f:
        pickle.dump(result, f)

def load_result():
    with open("result.pkl", "rb") as f:
        return pickle.load(f)

if __name__ == "__main__":
    main()

    result: TestSuiteResult = load_result()

    result.print_stats()
