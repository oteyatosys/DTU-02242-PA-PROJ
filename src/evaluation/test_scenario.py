from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Tuple, Union

from reader.method_signature import MethodSignature


@dataclass
class Deletion:
    file_path: Path
    line_range: Tuple[int, int]  # Tuple representing the start and end line numbers (inclusive)
    original_content: str = None  # Stores the original content that was deleted

    def __repr__(self):
        return f"Deletion(file_path={self.file_path}, line_range={self.line_range})"


@dataclass
class Addition:
    file_path: Path
    after_line: int  # Line number after which the new content will be inserted
    new_content: str  # Content to be inserted

    def __repr__(self):
        return f"Addition(file_path={self.file_path}, after_line={self.after_line})"


@dataclass
class TestStage:
    changes: List[Union[Deletion, Addition]] = field(default_factory=list)
    ground_truth: Set[MethodSignature] = field(default_factory=set)

    def __post_init__(self):
        changes = self.changes
        self.changes = []
        for change in changes:
            self.add_change(change)

    def _order_changes(self, dir: str = 'desc'):
        # Sort changes in descending order by starting line to avoid affecting subsequent changes
        self.changes.sort(key=lambda c: c.line_range[0] if isinstance(c, Deletion) else c.after_line + 1, reverse=(dir == 'desc'))

    def add_change(self, change: Union[Deletion, Addition]):
        if isinstance(change, Deletion):
            # Ensure no overlapping deletions are added
            for existing_change in self.changes:
                if (isinstance(existing_change, Deletion) and
                    change.file_path == existing_change.file_path and
                    not (change.line_range[1] < existing_change.line_range[0] or change.line_range[0] > existing_change.line_range[1])):
                    raise ValueError(f"Overlapping deletion detected: {change} overlaps with {existing_change}")
        elif isinstance(change, Addition):
            # Ensure no additions are added at invalid positions
            if change.after_line < 0:
                raise ValueError(f"Invalid line number {change.after_line} for addition: {change}")
        
        self.changes.append(change)
        self._order_changes('desc')

    def apply_changes(self, base_path: Path):
        self._order_changes('desc')
        for change in self.changes:
            file_to_change = base_path / change.file_path
            if isinstance(change, Deletion):
                if file_to_change.exists():
                    with file_to_change.open('r') as f:
                        lines = f.readlines()
                    start, end = change.line_range
                    start = start - 1
                    end = end - 1
                    if 0 <= start <= end < len(lines):
                        # Store the original content for reverting later
                        change.original_content = ''.join(lines[start:end + 1])
                        del lines[start:end + 1]
                        with file_to_change.open('w') as f:
                            f.writelines(lines)
                    else:
                        raise ValueError(f"Invalid line range {change.line_range} for file: {file_to_change}")
                else:
                    raise FileNotFoundError(f"File to modify does not exist: {file_to_change}")

            elif isinstance(change, Addition):
                if file_to_change.exists():
                    with file_to_change.open('r') as f:
                        lines = f.readlines()
                    after_line = change.after_line
                    if 0 <= after_line <= len(lines):
                        new_lines = change.new_content.lstrip('\n').splitlines(keepends=True)
                        lines = lines[:after_line] + new_lines + lines[after_line:]
                        with file_to_change.open('w') as f:
                            f.writelines(lines)
                    else:
                        raise ValueError(f"Invalid line number {after_line} for file: {file_to_change}")
                else:
                    raise FileNotFoundError(f"File to modify does not exist: {file_to_change}")

    def revert_changes(self, base_path: Path):
        # Sort changes in ascending order by starting line to revert correctly
        self._order_changes('asc')
        for change in self.changes:
            file_to_revert = base_path / change.file_path
            if isinstance(change, Deletion) and change.original_content is not None:
                if file_to_revert.exists():
                    with file_to_revert.open('r') as f:
                        lines = f.readlines()
                    start, end = change.line_range
                    start = start - 1
                    end = end - 1
                    if 0 <= start <= end <= len(lines):
                        lines[start:start] = change.original_content.splitlines(keepends=True)
                        with file_to_revert.open('w') as f:
                            f.writelines(lines)
                    else:
                        raise ValueError(f"Invalid line range {change.line_range} for file: {file_to_revert}")
                else:
                    raise FileNotFoundError(f"File to modify does not exist: {file_to_revert}")
            elif isinstance(change, Addition):
                if file_to_revert.exists():
                    with file_to_revert.open('r') as f:
                        lines = f.readlines()
                    after_line = change.after_line
                    new_lines_length = len(change.new_content.lstrip('\n').splitlines())
                    if 0 <= after_line < len(lines):
                        # Remove the added lines
                        lines = lines[:after_line] + lines[after_line + new_lines_length:]
                        with file_to_revert.open('w') as f:
                            f.writelines(lines)
                    else:
                        raise ValueError(f"Invalid line number {after_line} for file: {file_to_revert}")
                else:
                    raise FileNotFoundError(f"File to modify does not exist: {file_to_revert}")


@dataclass
class TestScenario:
    stages: List[TestStage] = field(default_factory=list)
