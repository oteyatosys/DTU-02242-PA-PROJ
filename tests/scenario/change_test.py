from pathlib import Path
from evaluation.test_scenario import Addition, Deletion, FindReplaceFirst, ReplaceLines, TestStage
import pytest

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
            ReplaceLines(
                file_rel, (2, 3),
                "Test\n"
            )
        ])

    # Apply changes
    test_scenario.apply_changes(base_path)
    modified_content = file_to_edit.read_text()
    expected_modified_content = """print('Hello World')
line 1
Test
line 6
Hej
"""
    assert modified_content == expected_modified_content

    # Revert changes
    test_scenario.revert_changes(base_path)
    reverted_content = file_to_edit.read_text()

    assert reverted_content == original_content

def test_overlapping_changes(tmp_path: Path):
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

    # Overlapping deletions are not allowed
    with pytest.raises(ValueError):
        TestStage([
            Deletion(
                file_rel, (4, 6)),
            Deletion(
                file_rel, (5, 6))
        ])

    # An addition after a line to be deleted is not allowed
    with pytest.raises(ValueError):
        TestStage([
            Deletion(
                file_rel, (3, 6)),
            Addition(
                file_rel, 4,
                "Hej\n"),
        ])

    # Same line additions are not allowed
    with pytest.raises(ValueError):
        TestStage([
            Addition(
                file_rel, 4,
                "Hej\n"),
            Addition(
                file_rel, 4,
                "Test\n"),
        ])

def test_find_replace(tmp_path: Path):
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
        FindReplaceFirst(
            file_rel,
            file_to_edit,
            "line 2", 
            "Hello World\n",
            2
        ),
    ])

    # Apply changes
    test_scenario.apply_changes(base_path)
    modified_content = file_to_edit.read_text()
    expected_modified_content = """line 1
Hello World
line 5
line 6
"""
    assert modified_content == expected_modified_content

    # Revert changes
    test_scenario.revert_changes(base_path)
    reverted_content = file_to_edit.read_text()

    assert reverted_content == original_content