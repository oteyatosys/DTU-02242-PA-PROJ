from reader.method_signature import MethodSignature

class Method:

    def __init__(self, class_name, json) -> None:
        self.class_name = class_name
        self.json = json
        self.name = json['name']
        self.bytecode = json['code']['bytecode']

        returns = Method.type_to_str(json["returns"])
        params = (Method.type_to_str(param) for param in json["params"])
        self.signature = MethodSignature(self.class_name, self.name, returns, params)

    @staticmethod
    def type_to_str(json):
        print(json)
        if json["type"] == None:
            return "void"
        elif "kind" in json['type'] and json['type']['kind'] == "class":
            return json['type']['name']
        elif "base" in json['type']:
            return json['type']['base']
        else:
            raise NotImplementedError(f"can't handle {json!r}")
