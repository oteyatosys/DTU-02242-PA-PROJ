from dataclasses import dataclass

@dataclass(frozen=True)
class MethodSignature:
    class_name: str
    name: str
    return_type: str
    parameters: tuple[str]
