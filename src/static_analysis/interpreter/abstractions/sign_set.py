from dataclasses import dataclass
from typing import Set, TypeAlias, Literal

from static_analysis.interpreter.abstractions.bot import Bot

Sign : TypeAlias = Literal["+"] | Literal["-"] | Literal["0"]

@dataclass
class SignSet(frozenset[Sign]):
    def __new__(cls, signs: Set[Sign] = set()):
        return super(SignSet, cls).__new__(cls, signs)

    def __init__(self, signs: Set[Sign] = set()):
        super().__init__()

    def __le__(self, other: 'SignSet') -> bool:
        return super().issubset(other)
    
    def __and__(self, other: 'SignSet') -> 'SignSet':
        return SignSet(super().__and__(other))
    
    def __or__(self, other: 'SignSet') -> 'SignSet':
        if isinstance(other, Bot):
            return self
        return SignSet(super().__or__(other))
    
    def __contains__(self, member: int):
        return super().__contains__('+' if member > 0 else '-' if member < 0 else '0')

    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self, value):
        return super().__eq__(value)
    
    def __repr__(self):
        return super().__repr__()

    def __sub__(self, other: 'SignSet') -> 'SignSet':
        return SignSet(super().__sub__(other))

    @staticmethod
    def abstract(items: set[int]):
        return SignSet(
            { "+" if item > 0 else "-" if item < 0 else "0" for item in items }
        )

    @staticmethod
    def bot() -> 'SignSet':
        return SignSet()
    
    @staticmethod
    def top() -> 'SignSet':
        return SignSet({ '+', '-', '0' })
