
from pathlib import Path
from evaluation.evaluator import Evaluator
from evaluation.results import TestSuiteResult
from evaluation.test_scenario import ReplaceLines, TestScenario, TestStage, TestSuite
from evaluation import TestSuiteBuilder
from prediction.abstract_sign_predictor import AbstractSignPredictor
from prediction.abstract_interval_predictor import AbstractIntervalPredictor
from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor
from evaluation.test_scenario_builder import TestSuiteBuilder
import pickle

from reader.method_signature import MethodSignature

project_root = Path(__file__).parent.parent

def main():
    evaluator = Evaluator(0)

    predictor: TestPredictor = AbstractIntervalPredictor()

    builder = TestSuiteBuilder(project_root / "java-example")

    # with builder.new_scenario() as scb:
    #     with scb.new_stage() as sb:
    #         sb.goto("org/example/Math.java", "int negate(int n)")
    #         sb.add("assert false;")
    #         sb.expect_fail("org.example.MathTest.testNegate:()V")
    #         sb.expect_fail("org.example.MathTest.testNegateNegative:()V")
    #         sb.expect_fail("org.example.MathTest.testNegateZero:()V")
    #         sb.expect_fail("org.example.MathTest.testAbsNegative:()V")

    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Math.java", "int abs(int n)")
            sb.add("assert false;")
            sb.expect_fail("org.example.MathTest.testAbs:()V")
            sb.expect_fail("org.example.MathTest.testAbsNegative:()V")
            sb.expect_fail("org.example.MathTest.testAbsZero:()V")

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
    