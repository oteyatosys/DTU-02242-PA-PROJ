
from pathlib import Path
from evaluation.evaluator import Evaluator
from evaluation.results import TestSuiteResult
from evaluation.test_scenario import ReplaceLines, TestScenario, TestStage, TestSuite
from prediction.abstract_predictor import AbstractPredictor
from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor
import pickle

from reader.method_signature import MethodSignature

project_root = Path(__file__).parent.parent

def main():
    evaluator = Evaluator()

    predictor: TestPredictor = AbstractPredictor()

    test_changeInt = TestScenario(
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

    test_invertBinaryOperation = TestScenario(
        project_root / "java-example", [
        TestStage([
            ReplaceLines(
                Path("org/example/App.java"), (12, 12),
"""
        return 5 + a;
"""
            ),
        ], {
        })
    ])
    test_changeOperator = TestScenario(
        project_root / "java-example", [
        TestStage([
            ReplaceLines(
                Path("org/example/App.java"), (37, 37),
"""
        while (i <= 1000000) i++;
"""
            ),
        ], {
            MethodSignature.from_str("org.example.AppTest.testSomeLoops:()V")
        })
    ])
    test_invertLine = TestScenario(
        project_root / "java-example", [
        TestStage([
            ReplaceLines(
                Path("org/example/App.java"), (46, 47),
"""
        if (i == 1) return 0;
        else if (i < 1) return 1;
"""
            ),
        ], {
            MethodSignature.from_str("org.example.AppTest.testInefficientFunction:()V"),
            MethodSignature.from_str("org.example.AppTest.testCallingInefficientFunction:()V")
        })
    ])
    test_addLine = TestScenario(
        project_root / "java-example", [
        TestStage([
            ReplaceLines(
                Path("org/example/App.java"), (56, 56),
"""
        n = n + 1; if (n == 238) return 100;
"""
            ),
        ], {
            MethodSignature.from_str("org.example.AppTest.testIsN238:()V")
        })
    ])

    test_changeFunctionCalled= TestScenario(
        project_root / "java-example", [
        TestStage([
            ReplaceLines(
                Path("org/example/App.java"), (42, 42),
"""
        return add5(convertBytesToBits(i)*i);
"""
            ),
        ], {
            MethodSignature.from_str("org.example.AppTest.testComplexFunction:()V"),
        })
    ])

    test_changeString= TestScenario(
        project_root / "java-example", [
        TestStage([
            ReplaceLines(
                Path("org/example/App.java"), (24, 24),
"""
        return greeting + ", " + name + "?";
"""
            ),
        ], {
            MethodSignature.from_str("org.example.AppTest.testGetgreetings1:()V"),
            MethodSignature.from_str("org.example.AppTest.testGetgreetings2:()V")
        })
    ])

    test_suite = TestSuite([       
        test_changeInt,
        test_invertBinaryOperation,
        test_changeOperator,
        test_invertLine,        
        test_addLine,
        test_changeFunctionCalled,
        #test_changeString
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
    