from reader.method_signature import MethodSignature

class Method:

    def __init__(self, class_name, json) -> None:
        self.class_name = class_name
        self.json = json
        self.name = json['name']
        self.bytecode = json['code']['bytecode']
        self.signature = MethodSignature.from_class_method(
            self.class_name, 
            self.name, 
            json["returns"],
            json["params"]
        )
