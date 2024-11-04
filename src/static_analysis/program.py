from typing import Dict, List
from static_analysis.method_id import MethodId
from pathlib import Path
import glob
import json
import jmespath
import logging

l = logging

class Program:
    def __init__(self, program: Dict[MethodId, List]):
        self._program = program

    def lookup(self, method_identifier: MethodId) -> list:
        return self._program[method_identifier]
    
    @staticmethod
    def parse_program(path: Path):
        files = Program.find_files_by_extension_from_root(path, "json")

        program = {}

        for file in files:
            with open(file, 'r') as file:
                data = json.load(file)

                class_name = data["name"]

                methods = {}
                
                res = jmespath.search(
                    "methods[*].{name: name, bytecode: code.bytecode, params: params[*].type, return_type: returns.type}", 
                    data
                )

                for method in res:
                    method_name = method["name"]

                    params = []

                    for param in method["params"]:
                        if not "kind" in param.keys():
                            params.append(param["base"])

                        elif param["kind"] == "array":

                            if "kind" in param["type"].keys():
                                l.debug(f"can't handle {param!r} - ignoring")
                            else:
                                params.append(f"{param["type"]["base"]}[]")
                                
                        else:
                            l.debug(f"can't handle {param!r} - ignoring")

                    return_type = method["return_type"]
                    bytecode = method["bytecode"]

                    if not method_name in methods.keys():
                        methods[method_name] = []

                    method_identifier = MethodId(
                        class_name,
                        method_name,
                        params,
                        return_type,
                    )

                    program[method_identifier] = bytecode

        return Program(program)

    @staticmethod
    def find_files_by_extension_from_root(root: Path, extension: str) -> list[str]:
        files = glob.glob(root.as_posix() + f"/**/*.{extension}", recursive=True)
        return files
