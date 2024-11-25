
from pathlib import Path
from evaluation.evaluator import Evaluator
from evaluation.results import TestSuiteResult
from prediction.abstract_predictor import AbstractPredictor
from prediction.itabstract_predictor import ItAbstractPredictor
from prediction.predictor import TestPredictor
from evaluation.test_scenario_builder import TestSuiteBuilder
import pickle

project_root = Path(__file__).parent.parent

def main():
    evaluator = Evaluator()

    predictor: TestPredictor = AbstractPredictor()

    builder = TestSuiteBuilder(project_root / "java-example")
    
    with builder.new_scenario() as scb:
        with scb.new_stage() as sb:
            sb.goto("org/example/Funs.java", "int zero()")
            sb.move(2)
            sb.replace("return 42;")
            sb.expect_change("org.example.FunsTest.testZero:()V")

    # with builder.new_scenario() as scb:
    #     with scb.new_stage() as sb:
    #         sb.goto("org/example/Funs.java", "int one()")
    #         sb.move(2)
    #         sb.replace("return 42;")
    #         sb.expect_change("org.example.FunsTest.testOne:()V")

    # with builder.new_scenario() as scb:
    #     with scb.new_stage() as sb:
    #         sb.goto("org/example/Funs.java", "int two()")
    #         sb.move(2)
    #         sb.replace("return 42;")
    #         sb.expect_change("org.example.FunsTest.testTwo:()V")

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
