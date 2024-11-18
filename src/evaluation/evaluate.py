
from pathlib import Path
from evaluation.evaluator import Evaluator
from evaluation.test_scenario import ReplaceLines, TestScenario, TestStage, TestSuite
from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor
from reader.method_signature import MethodSignature

project_root = Path(__file__).parent.parent.parent

def main():
    evaluator = Evaluator()

    predictor: TestPredictor = CallGraphPredictor()

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
    
    result = evaluator.evaluate_suite(predictor, test_suite)

    result.print_stats()

    avg_time = result.compute_average_time_taken_by_stage()
    print(f"Average time taken by stage: {avg_time}")
    time_variance = result.compute_average_time_taken_variance_by_stage()
    print(f"Average time taken variance by stage: {time_variance}")


if __name__ == "__main__":
    main()
