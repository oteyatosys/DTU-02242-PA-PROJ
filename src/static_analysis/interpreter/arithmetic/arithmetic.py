from typing import Generic, TypeVar

T = TypeVar('T')

class Arithmetic(Generic[T]):
    def binary(self, opr: str, a: T, b: T) -> T:
        pass

    def compare(self, opr: str, a: T, b: T) -> bool:
        pass
