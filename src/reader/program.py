from dataclasses import dataclass, field
from typing import Iterable, Tuple
from reader.file import File
from pathlib import Path
from reader.method import Method
from reader.method_signature import MethodSignature

@dataclass
class Program:
    files: dict[str, File] = field(default_factory=dict)
    test_files: dict[str, File] = field(default_factory=dict)

    @staticmethod
    def scan_files(target: dict[str, File], source_root_path: Path, bytecode_root_path: Path):
        for source_file in source_root_path.rglob("*.java"):
            bytecode_file = bytecode_root_path / source_file.relative_to(source_root_path).with_suffix(".json")
            file = File.from_path(source_file, bytecode_file)
            target[file.name] = file

    @staticmethod
    def load(data_dir: Path) -> 'Program':
        program = Program()
        Program.scan_files(program.files,      data_dir / "source",      data_dir / "bytecode")
        Program.scan_files(program.test_files, data_dir / "test-source", data_dir / "test-bytecode")
        return program

    # Returns a generator of all methods in the program
    def all_methods(self) -> Iterable[Tuple[File, Method]]:
        for file in self.files.values():
            for method in file.methods.values():
                yield file, method

    # Returns a generator of all test methods in the program
    def all_test_methods(self) -> Iterable[Tuple[File, Method]]:
        for file in self.test_files.values():
            for method in file.methods.values():
                if method.is_test():
                    yield file, method

    # Looks up a method by its signature by first checking the main files and then the test files
    # Raises KeyError if the method is not found
    def method(self, signature: MethodSignature) -> Method:
        if signature.class_name in self.files:
            return self.files[signature.class_name].methods[signature]
        elif signature.class_name in self.test_files:
            return self.test_files[signature.class_name].methods[signature]
        else:
            raise KeyError(f"Method {signature} not found in program")
    

    def contains_method(self, signature: MethodSignature) -> bool:
        try:
            self.method(signature)
            return True
        except KeyError:
            return False
