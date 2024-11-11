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
        return_type: str,
        parameters: tuple[str],
    ) -> 'MethodSignature':
        return MethodSignature(
            class_name,
            method_name,
            MethodSignature.type_to_str(return_type),
            tuple(MethodSignature.type_to_str(param) for param in parameters),
        )

    @staticmethod
    def from_bytecode(bytecode: dict) -> 'MethodSignature':
        method_name = bytecode["name"]
        class_name = bytecode["ref"]["name"]
        params = bytecode["args"]
        return_type = bytecode["returns"]

        return MethodSignature(
            class_name,
            method_name,
            MethodSignature.type_to_str(return_type),
            tuple(MethodSignature.type_to_str(param) for param in params),
        )
    
    @staticmethod
    def type_to_str(json):
        if not "type" in json:
            return json["name"]

        if json["type"] == None:
            return "void"
        elif "kind" in json['type'] and json['type']['kind'] == "class":
            return json['type']['name']
        elif "base" in json['type']:
            return json['type']['base']
        else:
            return json['type']['kind']
        
    def __str__(self):
        return f"{self.class_name}.{self.name}({', '.join(self.parameters)}) -> {self.return_type}"