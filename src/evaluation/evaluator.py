
from dataclasses import dataclass
from pathlib import Path
from typing import List

from evaluation.results import TestScenarioResult, TestStageResult, TestSuiteResult
from evaluation.test_scenario import Addition, Deletion, TestScenario, TestStage, TestSuite
from prediction.call_graph_predictor import CallGraphPredictor
from prediction.predictor import TestPredictor
from preparation.prepare import perform_data_rotation, reset_data
from reader.method_signature import MethodSignature
from reader.program import Program
import logging as l
from timeit import default_timer as timer, timeit

l.basicConfig(level=l.INFO)

data_dir = Path("data")
new_dir = data_dir / "new"
old_dir = data_dir / "old"

@dataclass
class Evaluator:
    def evaluate_suite(
        self,
        predictor: TestPredictor,
        test_suite: TestSuite
    ):
        results: List[TestScenarioResult] = []

        for test_scenario in test_suite.scenarios:
            results.append(
                self.evaluate_scenario(predictor, test_scenario)
            )

        return TestSuiteResult(
            results
        )

    def evaluate_scenario(
        self, 
        predictor: TestPredictor,
        test_scenario: TestScenario
    ) -> TestScenarioResult:
        maven_project = test_scenario.maven_project

        reset_data(maven_project)

        stage_results: List[TestStageResult] = []

        for stage in test_scenario.stages:
            stage_results.append(
                self.evaluate_stage(predictor, stage, maven_project)
            )

        return TestScenarioResult(stage_results)

    def evaluate_stage(
        self,
        predictor: TestPredictor,
        stage: TestStage,
        maven_project: Path
    ):
        src_dir = maven_project / "src/main/java"

        stage.apply_changes(src_dir)
        
        start_time = timer()

        perform_data_rotation(maven_project)

        ground_truth = stage.ground_truth

        new_program = Program.load(new_dir)
        old_program = Program.load(old_dir)
        
        predicted = predictor.predict(old_program, new_program)

        end_time = timer()

        stage.revert_changes(src_dir)

        return TestStageResult(
            predicted, ground_truth,
            end_time - start_time
        )
        

