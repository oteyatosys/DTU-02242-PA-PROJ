from dataclasses import dataclass
from jpamb_utils import JvmType, parse_params as jpamb_parse_params
from typing import Optional
import sys, logging

l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s")

@dataclass(frozen=True)
class MethodId:
    class_name: str
    method_name: str
    params: list[JvmType]
    return_type: Optional[JvmType]

    @staticmethod
    def parse(name):
        import re

        RE = (
            r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)"
        )
        if not (i := re.match(RE, name)):
            l.error("invalid method name: %r", name)
            sys.exit(-1)

        return MethodId(
            class_name=i["class_name"].replace('.','/'),
            method_name=i["method_name"],
            params=jpamb_parse_params(i["params"]),
            return_type=None if i["return"] == "V" else jpamb_parse_params([i["return"]])[0],
        )
    
    @staticmethod
    def parse_params(input_type: str) -> tuple[JvmType]:
        params = []
        while input_type:
            (tt, input_type) = MethodId.parse_type(input_type)
            params.append(tt)

        return tuple(params)

    @staticmethod
    def parse_type(input_type: str) -> tuple[JvmType, str]:
        assert input_type
        TYPE_LOOKUP: dict[str, JvmType] = {
            "Z": "boolean",
            "I": "int",
            "C": "char",
            "[I": "int[]",
            "[C": "char[]",
        }

        if input_type[0] in TYPE_LOOKUP:
            return (TYPE_LOOKUP[input_type[0]], input_type[1:])
        elif input_type[0] == "[":  # ]
            return (TYPE_LOOKUP[input_type[:2]], input_type[2:])
        else:
            raise ValueError(f"Unknown type {input_type}")

    def fully_qualified_signature(self) -> str:
        return f"{self.class_name}/{self.method_name}({','.join(self.params)})"

    @staticmethod
    def from_bytecode_invocation(bytecode: dict) -> 'MethodId':
        method_name = bytecode["method"]["name"]
        class_name = bytecode["method"]["ref"]["name"]
        params = bytecode["method"]["args"]
        return_type = bytecode["method"]["returns"]

        return MethodId(
            class_name,
            method_name,
            params,
            return_type
        )
    
    def match_signature(self, other: 'MethodId'):
        return\
            self.class_name == other.class_name\
            and self.method_name == other.method_name\
            and self.params == other.params

    def __eq__(self, other):
        return self.match_signature(other)
    
    def __hash__(self):
        return hash(self.fully_qualified_signature())
