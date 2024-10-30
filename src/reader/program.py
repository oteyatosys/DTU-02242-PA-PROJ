from reader.file import File
from pathlib import Path

class Program:
    def __init__(self, files: dict[str, File]):
        self.files = files

    @staticmethod
    def scan(source_root_path: Path, bytecode_root_path: Path) -> "Program":
        files = {}

        # Walk the source directory and assume that paths are the same for the bytecode
        for source_file in source_root_path.rglob("*.java"):
            bytecode_file = bytecode_root_path / source_file.relative_to(source_root_path).with_suffix(".json")
            file = File.from_path(source_file, bytecode_file)
            files[file.name] = file

        return Program(files)
