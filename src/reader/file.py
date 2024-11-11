import json

# I want a case class that can either be of type Class with a string name or Base with a string name

from reader.method import Method


class File:
    def __init__(self, name: str, source: str, bytecode: dict):
        self.name = name
        self.source = source
        self.bytecode = bytecode
        self.methods = {}
        self.scan_methods()

    @staticmethod
    def from_path(source_path: str, json_path: str) -> "File":
        with open(source_path, 'r') as source_file, open(json_path, 'r') as json_file:
            source = source_file.read()
            bytecode = json.load(json_file)
            name = bytecode["name"]
            return File(name, source, bytecode)

    def scan_methods(self):
        for method_json in self.bytecode["methods"]:
            method = Method(self.name, method_json)
            signature = method.signature
            self.methods[signature] = method

