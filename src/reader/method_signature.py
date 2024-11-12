from dataclasses import dataclass

@dataclass(frozen=True)
class MethodSignature:
    class_name: str
    name: str
    return_type: str
    parameters: tuple[str]

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
            MethodSignature.type_str(returns["type"]),
            tuple(MethodSignature.type_str(param["type"]) for param in params),
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
            MethodSignature.type_str(returns["type"]),
            tuple(MethodSignature.type_str(param["type"]) for param in params),
        )

    @staticmethod
    def type_str(type_json):
        if type_json == None:
            return "void"
        
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
