from reader.method_signature import MethodSignature
import jmespath

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

    # Returns true if the method has an annotation class that ends with 'Test'
    def is_test(self):
        return bool(jmespath.search("annotations[?ends_with(type, 'Test')]", self.json))
