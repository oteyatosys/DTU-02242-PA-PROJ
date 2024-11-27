from typing import Set

class RefSet:
    def __init__(self, elements: Set[str] = set()):
        self.elements = elements

    def __le__(self, other) -> bool:
        self.require_ref_set(other)
        return self.elements <= other.elements

    # Meet operation (intersection)
    def __and__(self, other):
        self.require_ref_set(other)
        return RefSet(self.elements & other.elements)

    # Join operation (union)
    def __or__(self, other):
        self.require_ref_set(other)
        return RefSet(self.elements | other.elements)

    def __hash__(self) -> int:
        return hash(frozenset(self.elements))

    def __eq__(self, other):
        self.require_ref_set(other)
        return self.elements == other.elements

    def __repr__(self) -> str:
        return f"{{{', '.join(sorted(self.elements))}}}"

    def require_ref_set(self, other):
        if not isinstance(other, RefSet):
            raise NotImplementedError("RefSet operation with non-RefSet")
