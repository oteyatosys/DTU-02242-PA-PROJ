
from pathlib import Path
from evaluation.evaluator import Evaluator
from evaluation.test_scenario import ReplaceLines, TestScenario, TestStage, TestSuite
from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor
from reader.method_signature import MethodSignature


def main():
    evaluator = Evaluator()

    predictor: TestPredictor = CallGraphPredictor()

    test_scenario1 = TestScenario(
        Path("java-example"), [
        TestStage([
            ReplaceLines(
                Path("org/example/App.java"), (20, 20),
"""
        return n == 0 ? 10 : n * factorial(n - 1);
"""
            ),
        ], {
            MethodSignature.from_str("org.example.AppTest.testFactorial:()V")
        })
    ])

    test_suite = TestSuite([
        test_scenario1
    ])
    
    result = evaluator.evaluate_suite(predictor, test_suite)

    result.print_stats()


if __name__ == "__main__":
    main()