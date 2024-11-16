from pathlib import Path
from evaluation.test_scenario import Change, TestStage

def test_apply_and_revert_changes(tmp_path: Path):
    # Setup
    base_path: Path = tmp_path / "base_code"
    base_path.mkdir()
    file_to_edit = base_path / "existing_file.py"
    original_content = """line 1
line 2
line 3
line 4
line 5
line 6
"""
    file_to_edit.write_text(original_content)

    # Create TestScenario
    test_scenario = TestStage([
            Change(
                file_to_edit, (1, 2), 
"""
print('Hello World')
"""),
            Change(
                file_to_edit, (4, 4), 
                "")
        ])

    # Apply changes
    test_scenario.apply_changes()
    modified_content = file_to_edit.read_text()
    expected_modified_content = """print('Hello World')
line 3
line 5
line 6
"""
    assert modified_content == expected_modified_content

    # Revert changes
    test_scenario.revert_changes()
    reverted_content = file_to_edit.read_text()

    assert reverted_content == original_content
