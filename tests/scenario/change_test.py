from pathlib import Path
from evaluation.test_scenario import Addition, Deletion, TestStage

def test_apply_and_revert_changes(tmp_path: Path):
    # Setup
    base_path: Path = tmp_path / "base_code"
    base_path.mkdir()
    file_rel = Path("existing_file.py")
    file_to_edit = base_path / file_rel
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
            Addition(
                file_rel, 0, 
                "print('Hello World')\n"),
            Deletion(
                file_rel, (4, 5)),
            Addition(
                file_rel, 6,
                "Hej\n"),
        ])

    # Apply changes
    test_scenario.apply_changes(base_path)
    modified_content = file_to_edit.read_text()
    expected_modified_content = """print('Hello World')
line 1
line 2
line 3
line 6
Hej
"""
    assert modified_content == expected_modified_content

    # Revert changes
    test_scenario.revert_changes(base_path)
    reverted_content = file_to_edit.read_text()

    assert reverted_content == original_content
