from dataclasses import dataclass
from typing import Any
from static_analysis.interpreter.abstractions import AbstractState
from reader import MethodSignature

@dataclass(frozen=True)
class NextState:
    next_state: AbstractState

@dataclass(frozen=True)
class ReturnValue:
    value: Any
    param_count: int

Action = NextState | ReturnValue

@dataclass(frozen=True)
class PC:
    signature: MethodSignature
    offset: int

    def __add__(self, i: int):
        return PC(self.signature, self.offset + i)
    
    def __sub__(self, i: int):
        return PC(self.signature, self.offset - i)
    
    def next(self) -> 'PC':
        return self + 1
    
    def prev(self) -> 'PC':
        return self - 1
    
    def jump(self, i: int) -> 'PC':
        return PC(self.signature, i)
    
    def __lt__(self, other: 'PC') -> bool:
        return self.signature < other.signature or self.offset < other.offset
