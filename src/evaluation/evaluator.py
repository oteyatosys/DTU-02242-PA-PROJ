
from dataclasses import dataclass
from pathlib import Path
from typing import List

from evaluation.results import TestScenarioResult, TestStageResult
from evaluation.test_scenario import Addition, Deletion, TestScenario, TestStage
from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor
from preparation.prepare import perform_data_rotation, reset_data
from reader.method_signature import MethodSignature
from reader.program import Program

data_dir = Path("data")
new_dir = data_dir / "new"
old_dir = data_dir / "old"

@dataclass
class Evaluator:
    maven_project: Path

    def evaluate(
        self, 
        predictor: TestPredictor,
        TestScenario: TestScenario
    ) -> TestScenarioResult:
        reset_data(self.maven_project)

        stage_results: List[TestStageResult] = []

        for stage in TestScenario.stages:
            src_dir = self.maven_project / "src/main/java"

            stage.apply_changes(src_dir)
            perform_data_rotation(self.maven_project)

            ground_truth = stage.ground_truth

            new_program = Program.load(new_dir)
            old_program = Program.load(old_dir)
            
            predicted = predictor.predict(old_program, new_program)

            stage.revert_changes(src_dir)

            stage_results.append(
                TestStageResult(
                    predicted, ground_truth
                )
            )

        return TestScenarioResult(stage_results)


def main():
    evaluator = Evaluator(
        Path("java-example")
    )

    predictor: TestPredictor = CallGraphPredictor()

    test_scenario = TestScenario([
        TestStage([
            Deletion(
                Path("org/example/App.java"), (20, 20)),
            Addition(
                Path("org/example/App.java"), 20,             
"""
        return n == 0 ? 10 : n * factorial(n - 1);
"""
            ),
        ], {
            MethodSignature.from_str("org.example.AppTest.testFactorial:()V")
        })
    ])
    
    result = evaluator.evaluate(predictor, test_scenario)

    print(result)


if __name__ == "__main__":
    main()