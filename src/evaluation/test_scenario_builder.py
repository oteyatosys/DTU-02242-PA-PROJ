from pathlib import Path
from evaluation.test_scenario import TestSuite, TestScenario, TestStage, Deletion, Addition, ReplaceLines
from reader.method_signature import MethodSignature
from contextlib import contextmanager

class TestSuiteBuilder:
    
    def __init__(self, java_project_path):
        self.java_project_path = java_project_path
        self.scenarios = []

    @contextmanager
    def new_scenario(self):
        scenario = TestScenario(self.java_project_path)
        yield TestScenarioBuilder(self, scenario)
        self.scenarios.append(scenario)
    
    def build(self):
        return TestSuite(self.scenarios)

class TestScenarioBuilder:

    def __init__(self, suite_builder, scenario):
        self.suite_builder = suite_builder
        self.scenario = scenario

    @contextmanager
    def new_stage(self):
        stage = TestStage([], None)
        yield TestStageBuilder(self, stage)
        self.scenario.stages.append(stage)

class TestStageBuilder:

    def __init__(self, stage_builder, stage):
        self.stage_builder = stage_builder
        self.stage = stage

        # Cursor state
        self.file_path = None
        self.line = 0

    def goto(self, file_path, search):
        self.line = self.find_line(file_path, search)
        self.file_path = file_path

    def move(self, line):
        self.line += line

    def delete(self, lines = 1):
        pos = (self.line, self.line + lines - 1)
        self.stage.add_change(Deletion(self.file_path, pos))

    def add(self, new_content):
        # Ensure that new_content ends with a newline
        if not new_content.endswith("\n"):
            new_content += "\n"
        self.stage.add_change(Addition(self.file_path, self.line, new_content))

    def replace(self, new_content, lines = 1):
        self.delete(lines)
        self.add(new_content)

    def expect_change(self, signature_str):
        signature = MethodSignature.from_str(signature_str)
        if self.stage.ground_truth is None:
            self.stage.ground_truth = {signature}
        else:
            self.stage.ground_truth.add(signature)

    # Search for a line in a file and return the line number
    def find_line(self, file_path, search):
        path = self.stage_builder.suite_builder.java_project_path / Path("src/main/java") / Path(file_path)
        with open(path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if search in line:
                    return i + 1
            raise Exception(f"Could not find line with search string '{search}' in file {self.get_path()}")
