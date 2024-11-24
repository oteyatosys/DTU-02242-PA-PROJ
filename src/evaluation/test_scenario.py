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
    
    def apply(self, base_path: Path):
        raise NotImplementedError
    
    def revert(self, base_path: Path):
        raise NotImplementedError


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
    
    def apply(self, base_path: Path):
        file_to_change = base_path / self.file_path
        if file_to_change.exists():
            with file_to_change.open('r') as f:
                lines = f.readlines()
            start, end = self.line_range
            start = start - 1
            end = end - 1

            if 0 <= start <= end < len(lines):
                # Store the original content for reverting later
                self.original_content = ''.join(lines[start:end + 1])
                del lines[start:end + 1]
                with file_to_change.open('w') as f:
                    f.writelines(lines)
            else:
                raise ValueError(f"Invalid line range {self.line_range} for file: {file_to_change}")
        else:
            raise FileNotFoundError(f"File to modify does not exist: {file_to_change}")

    def revert(self, base_path: Path):
        file_to_revert = base_path / self.file_path
        if file_to_revert.exists():
            with file_to_revert.open('r') as f:
                lines = f.readlines()
            start, end = self.line_range
            start = start - 1
            end = end - 1
            if 0 <= start <= end <= len(lines):
                lines[start:start] = self.original_content.splitlines(keepends=True)
                with file_to_revert.open('w') as f:
                    f.writelines(lines)
            else:
                raise ValueError(f"Invalid line range {self.line_range} for file: {file_to_revert}")
        else:
            raise FileNotFoundError(f"File to modify does not exist: {file_to_revert}")

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
    
    def apply(self, base_path: Path):
        file_to_change = base_path / self.file_path
        if file_to_change.exists():
            with file_to_change.open('r') as f:
                lines = f.readlines()
            after_line = self.after_line
            if 0 <= after_line <= len(lines):
                new_lines = self.new_content.lstrip('\n').splitlines(keepends=True)
                lines = lines[:after_line] + new_lines + lines[after_line:]
                with file_to_change.open('w') as f:
                    f.writelines(lines)
            else:
                raise ValueError(f"Invalid line number {after_line} for file: {file_to_change}")
        else:
            raise FileNotFoundError(f"File to modify does not exist: {file_to_change}")

    def revert(self, base_path):
        file_to_revert = base_path / self.file_path
        if file_to_revert.exists():
            with file_to_revert.open('r') as f:
                lines = f.readlines()
            after_line = self.after_line
            new_lines_length = len(self.new_content.lstrip('\n').splitlines())
            if 0 <= after_line < len(lines):
                # Remove the added lines
                lines = lines[:after_line] + lines[after_line + new_lines_length:]
                with file_to_revert.open('w') as f:
                    f.writelines(lines)
            else:
                raise ValueError(f"Invalid line number {after_line} for file: {file_to_revert}")
        else:
            raise FileNotFoundError(f"File to modify does not exist: {file_to_revert}")

    def __repr__(self):
        return f"Addition(file_path={self.file_path}, after_line={self.after_line})"


@dataclass
class DecomposableChange(ABC):
    def decompose(self) -> List[Addition|Deletion]:
        raise NotImplementedError

@dataclass
class ReplaceLines(DecomposableChange):
    file_path: Path
    line_range: Tuple[int, int]
    new_content: str

    def decompose(self) -> List[Addition|Deletion]:
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

# This class is not very nice, because it also requires the actual path to the file
@dataclass
class FindReplaceFirst(DecomposableChange):
    file_path: Path
    actual_path: Path
    search_line: str
    new_content: str
    delelete_following: int = 0
    _replace_lines: ReplaceLines = field(init=False)

    def __post_init__(self):
        # find line index of the line to replace
        
        # read the file
        with open(self.actual_path, 'r') as f:
            lines = f.readlines()
        
        # find the line index
        line_index = -1
        for i, line in enumerate(lines):
            # Only has to match part of the line
            if self.search_line in line:
                line_index = i + 1
                break

        self._replace_lines = ReplaceLines(
            file_path=self.file_path,
            line_range=(line_index, line_index + self.delelete_following),
            new_content=self.new_content
        )

    def decompose(self) -> List[Addition|Deletion]:
        return self._replace_lines.decompose()


class TestStage:
    def __init__(self, changes: List[Union[Change, DecomposableChange]] = [], ground_truth: Set[MethodSignature] = None):
        self.ground_truth: Set[MethodSignature] = ground_truth

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
        # In case of same key, additions should come before deletions
        self.changes.sort(key=lambda c: (c.order_key(), isinstance(c, Deletion)), reverse=(dir == 'desc'))


    def add_changes(self, changes: List[Addition|Deletion]):
        for change in changes:
            self.add_change(change)


    def add_change(self, change: Addition|Deletion):
        if change.lower() < 0:
            raise ValueError(f"Invalid line number {change.lower()} for change: {change}")
        
        if change.upper() < change.lower():
            raise ValueError(f"Invalid line range {change.lower()}:{change.upper} for change: {change}")

        for existing_change in self.changes:
            left, right = (change, existing_change) if isinstance(change, Addition) else (existing_change, change)
            if (
                # Ensure no overlapping deletions are added
                isinstance(left, Deletion) and isinstance(right, Deletion) and
                left.file_path == right.file_path and
                not (left.upper() < right.lower() or left.lower() > right.upper())
            ):
                raise ValueError(f"Overlapping deletion detected: {change} overlaps with {existing_change}")
            elif (
                # Ensure no overlapping additions are added
                isinstance(left, Addition) and isinstance(right, Addition) and
                left.file_path == right.file_path and
                left.lower() == right.lower()
            ):
                raise ValueError(f"Overlapping addition detected: {change} overlaps with {existing_change}")
            elif (
                # Ensure no overlapping addition and deletion are added
                isinstance(left, Addition) and
                left.file_path == right.file_path and
                not (left.upper() < right.lower() or left.lower() >= right.upper())
            ):
                raise ValueError(f"Overlapping addition detected: {change} overlaps with {existing_change}")

        self.changes.append(change)


    def apply_changes(self, base_path: Path):
        # Sort changes in descending order by starting line to avoid affecting subsequent changes
        self._order_changes('desc')
        for change in self.changes:
            change.apply(base_path)


    def revert_changes(self, base_path: Path):
        # Sort changes in ascending order by starting line to revert correctly
        self._order_changes('asc')
        for change in self.changes:
            change.revert(base_path)


@dataclass
class TestScenario:
    maven_project: Path
    stages: List[TestStage] = field(default_factory=list)


@dataclass
class TestSuite:
    scenarios: List[TestScenario] = field(default_factory=list)