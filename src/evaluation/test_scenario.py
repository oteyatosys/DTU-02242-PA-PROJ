

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple

from reader.method_signature import MethodSignature


@dataclass
class Change:
    file_path: Path
    line_range: Tuple[int, int]  # Tuple representing the start and end line numbers (inclusive)
    new_content: str  # New content to replace the specified line range
    original_content: str = None  # Stores the original content that was replaced

    def __repr__(self):
        return f"Change(file_path={self.file_path}, line_range={self.line_range})"
    

@dataclass
class TestStage:
    changes: List[Change] = field(default_factory=list)
    ground_truth: Set[MethodSignature] = field(default_factory=set)

    def __post_init__(self):
        changes = self.changes
        self.changes = []
        for change in changes:
            self.add_change(change)

    def _order_changes(self):
        # Sort changes in descending order by line range to avoid affecting subsequent changes
        self.changes.sort(key=lambda c: c.line_range[0], reverse=True)

    def add_change(self, change: Change):
        # Ensure no overlapping changes are added
        for existing_change in self.changes:
            if (change.file_path == existing_change.file_path and
                not (change.line_range[1] < existing_change.line_range[0] or change.line_range[0] > existing_change.line_range[1])):
                raise ValueError(f"Overlapping change detected: {change} overlaps with {existing_change}")
        
        self.changes.append(change)
        self._order_changes()

    def apply_changes(self):
        for change in self.changes:
            file_to_change = change.file_path
            if file_to_change.exists():
                with file_to_change.open('r') as f:
                    lines = f.readlines()
                start, end = change.line_range
                start = start - 1
                end = end - 1
                if 0 <= start <= end < len(lines):
                    # Store the original content for reverting later
                    change.original_content = ''.join(lines[start:end + 1])
                    new_lines = change.new_content.lstrip('\n').splitlines(keepends=True)
                    lines[start:end + 1] = new_lines
                    with file_to_change.open('w') as f:
                        f.writelines(lines)
                else:
                    raise ValueError(f"Invalid line range {change.line_range} for file: {file_to_change}")
            else:
                raise FileNotFoundError(f"File to modify does not exist: {file_to_change}")

    def revert_changes(self):
        for change in reversed(self.changes):
            if change.original_content is not None:
                file_to_revert = change.file_path
                if file_to_revert.exists():
                    with file_to_revert.open('r') as f:
                        lines = f.readlines()
                    start, end = change.line_range
                    start = start - 1
                    end = end - 1
                    if 0 <= start <= end < len(lines):
                        lines[start:end] = change.original_content.splitlines(keepends=True)
                        with file_to_revert.open('w') as f:
                            f.writelines(lines)
                    else:
                        raise ValueError(f"Invalid line range {change.line_range} for file: {file_to_revert}")
                else:
                    raise FileNotFoundError(f"File to modify does not exist: {file_to_revert}")
                

@dataclass
class TestScenario:
    stages: List[TestStage] = field(default_factory=list)