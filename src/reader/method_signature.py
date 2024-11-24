from dataclasses import dataclass
import sys

@dataclass(frozen=True)
class MethodSignature:
    class_name: str
    name: str
    return_type: str
    parameters: tuple[str]

    def __lt__(self, other: 'MethodSignature') -> bool:
        return str(self) < str(other)

    @staticmethod
    def from_class_method(
        class_name: str,
        method_name: str,
        returns: dict,
        params: list[dict],
    ) -> 'MethodSignature':
        return MethodSignature(
            class_name,
            method_name,
            MethodSignature.type_str(returns),
            tuple(MethodSignature.type_str(param) for param in params),
        )


    @staticmethod
    def from_str(shortform: str):
        import re

        RE = (
            r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)"
        )
        if not (i := re.match(RE, shortform)):
            print("invalid method name: %r", shortform)
            sys.exit(-1)

        type_map = {
            "I": "int",
            "C": "char",
            "V": "void",
        }

        return MethodSignature(
            class_name=i["class_name"].replace('.','/'),
            name=i["method_name"],
            parameters=tuple(type_map[j] for j in i["params"]),
            return_type=type_map[i["return"]],
        )


    @staticmethod
    def from_bytecode(bytecode: dict) -> 'MethodSignature':
        method_name = bytecode["name"]
        class_name = bytecode["ref"]["name"]
        params = bytecode["args"]
        returns = bytecode["returns"]

        return MethodSignature(
            class_name,
            method_name,
            MethodSignature.invocation_type_str(returns),
            tuple(MethodSignature.invocation_type_str(param) for param in params),
        )


    @staticmethod
    def invocation_type_str(json):
        if json is None:
            return "void"
        
        if "kind" in json:
            return MethodSignature.type_str(json)
        
        if isinstance(json, str):
            return json
        
        raise NotImplementedError(f"Type {json!r} not implemented")


    @staticmethod
    def type_str(json):
        if json == None or "type" in json and json["type"] == None:
            return "void"
        
        if "type" in json:
            type_json = json["type"]
        else:
            type_json = json

        if "base" in type_json:
            return type_json["base"]
        
        kind = type_json["kind"]

        if kind == "class":
            return type_json["name"]
        elif kind == "array":
            return f"{MethodSignature.type_str(type_json['type'])}[]"
        
        raise NotImplementedError(f"Type {type_json!r} not implemented")

    def __str__(self):
        return f"{self.class_name}.{self.name}({', '.join(self.parameters)}) -> {self.return_type}"

    def __repr__(self):
        return str(self)
