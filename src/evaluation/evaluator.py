
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
from typing import List, Set, Tuple
from evaluation.results import TestScenarioResult, TestStageResult, TestSuiteResult
from evaluation.test_scenario import TestScenario, TestStage, TestSuite
from prediction.predictor import TestPredictor
from preparation.prepare import perform_data_rotation, reset_data
from reader.method_signature import MethodSignature
from reader.program import Program
import logging as l
from timeit import default_timer as timer
import os
from xml.etree import ElementTree as ET
import tempfile
import tqdm

project_root = Path(__file__).parent.parent.parent
project_tmp_dir = project_root / "tmp"

l.basicConfig(level=l.INFO)

@dataclass
class Evaluator:
    max_workers: int = 7

    def evaluate_suite(
        self,
        predictor: TestPredictor,
        test_suite: TestSuite
    ) -> TestSuiteResult:

        results: List[TestScenarioResult] = []

        total_stages = sum(len(scenario.stages) for scenario in test_suite.scenarios)
        progress_bar = tqdm.tqdm(total=total_stages, desc="Scenarios", position=0)

        start = timer()

        if self.max_workers == 0:
            for scenario in test_suite.scenarios:
                result = self.evaluate_scenario(predictor, scenario, progress_bar)
                results.append(result)
        else: 
            with ThreadPoolExecutor(max_workers = self.max_workers) as executor:
                future_to_scenario = {
                    executor.submit(self.evaluate_scenario, predictor, scenario, progress_bar): scenario
                    for scenario in test_suite.scenarios
                }

                for future in as_completed(future_to_scenario):
                    result: TestScenarioResult = future.result()
                    results.append(result)
        
        end = timer()

        progress_bar.close()

        return TestSuiteResult(
            results,
            end - start
        )

    def evaluate_scenario(
        self, 
        predictor: TestPredictor,
        test_scenario: TestScenario,
        progress_bar: tqdm.tqdm
    ) -> TestScenarioResult:
        maven_project = test_scenario.maven_project

        project_tmp_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=project_tmp_dir) as tmp_dir:
            tmp_dir = Path(tmp_dir)

            maven_project_copy = tmp_dir / maven_project.name
            shutil.copytree(maven_project, maven_project_copy)

            data_dir = tmp_dir / "data"

            reset_data(maven_project_copy, data_dir)

            stage_results: List[TestStageResult] = []

            for stage in test_scenario.stages:
                stage_results.append(
                    self.evaluate_stage(predictor, stage, maven_project_copy, data_dir)
                )
                progress_bar.update(1)

            return TestScenarioResult(stage_results)

    def evaluate_stage(
        self,
        predictor: TestPredictor,
        stage: TestStage,
        maven_project: Path,
        data_dir: Path
    ) -> TestStageResult:
        old_dir = data_dir / "old"
        new_dir = data_dir / "new"
        src_dir = maven_project / "src/main/java"

        stage.apply_changes(src_dir)
        
        perform_data_rotation(maven_project, data_dir)

        start_time = timer()
        
        ground_truth_positive: Set[MethodSignature] = stage.ground_truth

        new_program: Program = Program.load(new_dir)
        old_program: Program = Program.load(old_dir)
        
        predicted = predictor.predict(old_program, new_program)

        end_time = timer()
        prediction_time = end_time - start_time

        non_passing_tests: Set[MethodSignature] = None
        all_test_time = None

        if stage.ground_truth is None:

            start_time = timer()
            
            subprocess.run(
                ["mvn", "-q", "-f", str(maven_project / "pom.xml"), "surefire:test", "-Dsurefire.printSummary=true"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            end_time = timer()
            all_test_time = end_time - start_time

            ground_truth_positive = self._extract_non_passing_tests(maven_project / "target/surefire-reports")

        dtest_param = self._compute_dtest_param(predicted)

        start_time = timer()

        subprocess.run(
            ["mvn", "-q", "-f", str(maven_project / "pom.xml"), f"surefire:test", f"-Dtest={dtest_param}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        end_time = timer()
        subset_test_time = end_time - start_time

        stage.revert_changes(src_dir)

        all_test_signatures: Set[MethodSignature] = {method.signature for (_, method) in new_program.all_test_methods()}
        ground_truth_negative = all_test_signatures - ground_truth_positive

        return TestStageResult(
            predicted, 
            ground_truth_positive,
            ground_truth_negative,
            non_passing_tests,
            prediction_time,
            all_test_time,
            subset_test_time
        )

    def _compute_dtest_param(self, predicted: Set[MethodSignature]) -> str:
        same_class_methods: dict[str, str] = {}

        for signature in predicted:
            if signature.class_name not in same_class_methods:
                same_class_methods[signature.class_name] = set()
            same_class_methods[signature.class_name].add(signature.name)

        params = [
            f"{k}#{"+".join(v)}" for k, v in same_class_methods.items()
        ]

        return ",".join(params)

    def _extract_test_results(self, report_dir) -> List[Tuple[MethodSignature, str]]:
        results: List[Tuple[MethodSignature, str]] = []
        for file in os.listdir(report_dir):
            if file.startswith("TEST-") and file.endswith(".xml"):
                tree = ET.parse(os.path.join(report_dir, file))
                for testcase in tree.findall(".//testcase"):
                    name = testcase.get("name")
                    classname = testcase.get("classname")
                    if testcase.find("failure") is not None:
                        status = "FAILED"
                    elif testcase.find("error") is not None:
                        status = "ERROR"
                    else:
                        status = "PASSED"

                    # Assuming void and no arguments
                    signature: MethodSignature = MethodSignature(
                        classname.replace(".", "/"),
                        name, "void", ()
                    )

                    results.append((signature, status))
        return results


    def _extract_non_passing_tests(self, report_dir) -> Set[MethodSignature]:
        results = self._extract_test_results(report_dir)

        results = {signature for (signature, status) in results if status != "PASSED"}

        return results
