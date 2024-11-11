from typing import Generator, Tuple
from reader.file import File
from pathlib import Path
from reader.method import Method
from reader.method_signature import MethodSignature

class Program:
    def __init__(self, files: dict[str, File] = {}, test_files: dict[str, File] = {}):
        self.files = files
        self.test_files = test_files

    @staticmethod
    def scan(source_root_path: Path, bytecode_root_path: Path) -> "Program":
        return Program().scan(source_root_path, bytecode_root_path)

    def scan(self, source_root_path: Path, bytecode_root_path: Path):
        # Walk the source directory and assume that paths are the same for the bytecode
        for source_file in source_root_path.rglob("*.java"):
            bytecode_file = bytecode_root_path / source_file.relative_to(source_root_path).with_suffix(".json")
            file = File.from_path(source_file, bytecode_file)
            self.files[file.name] = file
        return self
    
    def scan_tests(self, test_source_root_path: Path, test_bytecode_root_path: Path):
        # Walk the test source directory and assume that paths are the same for the test bytecode
        for source_file in test_source_root_path.rglob("*.java"):
            bytecode_file = test_bytecode_root_path / source_file.relative_to(test_source_root_path).with_suffix(".json")
            file = File.from_path(source_file, bytecode_file)
            self.test_files[file.name] = file
        return self

    def all_methods(self) -> Generator[Tuple[File, Method], None, None]:
        for file in self.files.values():
            for method in file.methods.values():
                yield file, method

    def method(self, signature: MethodSignature):
        return self.files[signature.class_name].methods[signature]
