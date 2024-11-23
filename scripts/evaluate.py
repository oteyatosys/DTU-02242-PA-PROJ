
from pathlib import Path
from evaluation.evaluator import Evaluator
from evaluation.results import TestSuiteResult
from evaluation.test_scenario import ReplaceLines, TestScenario, TestStage, TestSuite
from prediction.abstract_predictor import AbstractPredictor
from prediction.predictor import TestPredictor
import pickle

from reader.method_signature import MethodSignature

project_root = Path(__file__).parent.parent

def main():
    evaluator = Evaluator()

    predictor: TestPredictor = AbstractPredictor()

    test_scenario1 = TestScenario(
        project_root / "java-example", [
        TestStage([
            ReplaceLines(
                Path("org/example/App.java"), (24, 24),
"""
        return n == 0 ? 10 : n * factorial(n - 1);
"""
            ),
        ], {
            MethodSignature.from_str("org.example.AppTest.testFactorial:()V")
        })
    ])

    test_suite = TestSuite([
        test_scenario1,
    ])
    
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
    