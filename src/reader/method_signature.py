from dataclasses import dataclass

@dataclass(Frozen=True)
class MethodSignature:
    class_name: str
    name: str
    return_type: str
    parameters: tuple[str]
