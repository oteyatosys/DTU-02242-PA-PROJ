import json

class File:
    def __init__(self, name: str, source: str, bytecode: dict):
        self.name = name
        self.source = source
        self.bytecode = bytecode

    @staticmethod
    def from_path(source_path: str, json_path: str) -> "File":
        with open(source_path, 'r') as source_file, open(json_path, 'r') as json_file:
            source = source_file.read()
            bytecode = json.load(json_file)
            name = bytecode["name"]
            return File(name, source, bytecode)

    # def method(self, name: str):
    #     return self.bytecode["methods"][method_id]
