from dataclasses import dataclass
from typing import Union

from static_analysis.interpreter.abstractions.bool_set import BoolSet
from static_analysis.interpreter.abstractions.sign_set import SignSet

AbstractValue = Union[SignSet, BoolSet]

@dataclass
class AbstractState:
    stack: list[AbstractValue]
    locals: dict[int, AbstractValue]
    done: str = None

    def __le__(self, other: 'AbstractState') -> bool:
        self.ensure_compatability(other)
        stack_le = all(s1 <= s2 for s1, s2 in zip(self.stack, other.stack))
        locals_le = all(
            self.locals.get(key) <= other.locals.get(key)
            for key in set(self.locals) | set(other.locals)
        )
        return stack_le and locals_le

    # Meet operation
    def __and__(self, other: 'AbstractState') -> 'AbstractState':
        self.ensure_compatability(other)
        stack_meet = [s1 & s2 for s1, s2 in zip(other.stack, self.stack)]
        locals_meet = {
            key: self.locals.get(key) & other.locals.get(key)
            for key in set(self.locals) | set(other.locals)
        }
        return AbstractState(stack=stack_meet, locals=locals_meet)
    
    # Join operation
    def __or__(self, other: 'AbstractState') -> 'AbstractState':
        self.ensure_compatability(other)
        stack_join = [s1 | s2 for s1, s2 in zip(other.stack, self.stack)]
        locals_join = {
            key: self.locals.get(key) | other.locals.get(key)
            for key in set(self.locals) | set(other.locals)
        }
        return AbstractState(stack=stack_join, locals=locals_join)

    def copy(self):
        return AbstractState(
            stack=self.stack.copy(), 
            locals=self.locals.copy(),
        )
    
    def __hash__(self) -> int:
        return hash((tuple(self.stack), tuple(self.locals), self.done))
    
    def __eq__(self, other: 'AbstractState') -> bool:
        self.ensure_compatability(other)
        return self.stack == other.stack\
            and self.locals == other.locals\
            and self.done == other.done

    # Ensure that the two states are compatible for comparison, meet, and join operations
    def ensure_compatability(self, other: 'AbstractState'):
        if len(self.stack) != len(other.stack):
            raise ValueError("Stacks must be of the same length")
        if len(self.locals) != len(other.locals):
            raise ValueError("Locals must be of the same length")
        

    @staticmethod
    def bot():
        return AbstractState([], {})
    

    