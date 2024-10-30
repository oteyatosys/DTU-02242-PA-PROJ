from dataclasses import dataclass
from typing import TypeAlias, Literal

Sign : TypeAlias = Literal["+"] | Literal["-"] | Literal["0"]

@dataclass
class SignSet:
    signs : set[Sign]

    @staticmethod
    def abstract(items : set[int]):
        return SignSet({ "+" if i > 0 else "-" if i < 0 else "0" for i in items })

    # Checks if an int is contained in the set
    def __contains__(self, member: int):
        if member > 0: 
            return "+" in self.signs
        elif member < 0:
            return "-" in self.signs
        else:
            return "0" in self.signs

    def __le__(self, other):
        return self.signs.issubset(other.signs)
  
    def __and__(self, other):
        return SignSet(self.signs & other.signs)
  
    def __or__(self, other):
        return SignSet(self.signs | other.signs)
    
    def __str__(self) -> str:
        return f"{self.signs}"
    
    def __repr__(self) -> str:
        return f"{self.signs}"

    @staticmethod
    def bot():
        return SignSet(set())
    
    @staticmethod
    def top():
        return SignSet({ "+", "-", "0" })

from hypothesis import given
from hypothesis.strategies import integers, sets

@given(sets(integers()))
def test_valid_abstraction(xs):
    s = SignSet.abstract(xs) 
    assert all(x in s for x in xs)
