from dataclasses import dataclass
import jpamb_utils
from jpamb_utils import JvmType
from typing import Optional
import sys, logging

l = logging

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
            params=jpamb_utils.parse_params(i["params"]),
            return_type=None if i["return"] == "V" else jpamb_utils.parse_params([i["return"]])[0],
        )
    
    def params_to_str(self) -> str:
        return ','.join(map(str, self.params))

    def fully_qualified_signature(self) -> str:
        return f"{self.class_name}/{self.method_name}({self.params_to_str()})"

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
