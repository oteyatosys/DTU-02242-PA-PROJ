
from pathlib import Path
from evaluation.evaluator import Evaluator
from evaluation.results import TestSuiteResult
from evaluation.test_scenario import ReplaceLines, TestScenario, TestStage, TestSuite
from prediction.abstract_predictor import AbstractPredictor
from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor
from evaluation.test_scenario_builder import TestSuiteBuilder
import pickle

from reader.method_signature import MethodSignature

project_root = Path(__file__).parent.parent

def main():
    evaluator = Evaluator()

    predictor: TestPredictor = AbstractPredictor()

    builder = TestSuiteBuilder(project_root / "java-example")
    
    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Funs.java", "public static int one()")
            sb.move(2)
            sb.replace("return 42;")
            sb.expect_change("org.example.FunsTest.testRun1:()V")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Funs.java", "public static int two()")
            sb.move(2)
            sb.replace("return 42;")
            sb.expect_change("org.example.FunsTest.testRun2:()V")

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

    # result: TestSuiteResult = load_result()

    # result.print_stats()
