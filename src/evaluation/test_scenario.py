from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Tuple, Union

from reader.method_signature import MethodSignature


@dataclass
class Change(ABC):
    file_path: Path

    def order_key(self) -> int:
        raise NotImplementedError

    def upper() -> int:
        raise NotImplementedError
    
    def lower() -> int:
        raise NotImplementedError

@dataclass
class DecomposableChange(ABC):
    def decompose(self) -> List[Change]:
        raise NotImplementedError

@dataclass
class ReplaceLines(DecomposableChange):
    file_path: Path
    line_range: Tuple[int, int]
    new_content: str

    def decompose(self) -> List[Change]:
        return [
            Deletion(
                file_path=self.file_path,
                line_range=self.line_range
            ),
            Addition(
                file_path=self.file_path,
                after_line=self.line_range[1],
                new_content=self.new_content
            )
        ]

@dataclass
class Deletion(Change):
    file_path: Path
    line_range: Tuple[int, int]  # Tuple representing the start and end line numbers (inclusive)
    original_content: str = None  # Stores the original content that was deleted

    def order_key(self) -> int:
        return self.line_range[0]
    
    def upper(self) -> int:
        return self.line_range[1]
    
    def lower(self) -> int:
        return self.line_range[0]

    def __repr__(self):
        return f"Deletion(file_path={self.file_path}, line_range={self.line_range})"


@dataclass
class Addition(Change):
    file_path: Path
    after_line: int  # Line number after which the new content will be inserted
    new_content: str  # Content to be inserted

    def order_key(self) -> int:
        return self.after_line + 1
    
    def upper(self) -> int:
        return self.after_line
    
    def lower(self) -> int:
        return self.after_line

    def __repr__(self):
        return f"Addition(file_path={self.file_path}, after_line={self.after_line})"


class TestStage:
    def __init__(self, changes: List[Union[Change, DecomposableChange]] = [], ground_truth: Set[MethodSignature] = {}):
        self.ground_truth = {}
        self.ground_truth.update(ground_truth)

        self.changes: List[Change] = []
        for change in changes:
            match change:
                case DecomposableChange():
                    self.add_changes(change.decompose())
                case Change():
                    self.add_change(change)
                case _:
                    raise ValueError(f"Invalid change type: {change}")    


    def _order_changes(self, dir: str = 'desc'):
        # Sort changes in descending order by starting line to avoid affecting subsequent changes
        self.changes.sort(key=lambda c: (c.order_key(), isinstance(c, Deletion)), reverse=(dir == 'desc'))


    def add_changes(self, changes: List[Union[Change]]):
        for change in changes:
            self.add_change(change)


    def add_change(self, change: Union[Change]):
        if change.lower() < 0:
            raise ValueError(f"Invalid line number {change.lower()} for change: {change}")
        
        if change.upper() < change.lower():
            raise ValueError(f"Invalid line range {change.lower()}:{change.upper} for change: {change}")

        for existing_change in self.changes:
            # Ensure no overlapping deletions are added
            if (
                isinstance(change, Deletion) and
                change.file_path == existing_change.file_path and
                not (change.upper() < existing_change.lower() or change.lower() > existing_change.upper())
            ):
                raise ValueError(f"Overlapping deletion detected: {change} overlaps with {existing_change}")
        
        self.changes.append(change)


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


    def _revert_deletion(self, change: Deletion, file_to_revert: Path):
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
    
    def _revert_addition(self, change: Addition, file_to_revert: Path):
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

    def revert_changes(self, base_path: Path):
        # Sort changes in ascending order by starting line to revert correctly
        self._order_changes('asc')
        for change in self.changes:
            file_to_revert = base_path / change.file_path
            match change:
                case Deletion():
                    self._revert_deletion(change, file_to_revert)
                case Addition():
                    self._revert_addition(change, file_to_revert)
                case _:
                    raise ValueError(f"Invalid change type: {change}")



@dataclass
class TestScenario:
    maven_project: Path
    stages: List[TestStage] = field(default_factory=list)


@dataclass
class TestSuite:
    scenarios: List[TestScenario] = field(default_factory=list)