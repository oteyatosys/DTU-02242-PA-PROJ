from typing import Generic, TypeVar

T = TypeVar('T')

class Arithmetic(Generic[T]):
    def binary(self, opr: str, a: T, b: T) -> T:
        raise NotImplementedError

    def compare(self, opr: str, a: T, b: T) -> bool:
        raise NotImplementedError

    def negate(self, a: T) -> T:
        raise NotImplementedError