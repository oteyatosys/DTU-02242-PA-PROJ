from dataclasses import dataclass

@dataclass
class BoolSet(frozenset[bool]):
    def __new__(cls, *init: bool):
        return super(BoolSet, cls).__new__(cls, init)

    def __init__(self, *init: bool):
        super().__init__()

    def __and__(self, other: 'BoolSet') -> 'BoolSet':
        return BoolSet(*(super().__and__(other)))

    def __or__(self, other: 'BoolSet') -> 'BoolSet':
        return BoolSet(*(super().__or__(other)))

    def __le__(self, other: 'BoolSet') -> bool:
        return self <= other
    
    def __repr__(self):
        return super().__repr__()
    
    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self, value):
        return super().__eq__(value)

    @staticmethod
    def abstract(items: set[bool]):
        return BoolSet(items)

    @staticmethod
    def bot() -> 'BoolSet':
        return BoolSet()

    @staticmethod
    def top() -> 'BoolSet':
        return BoolSet(True, False)