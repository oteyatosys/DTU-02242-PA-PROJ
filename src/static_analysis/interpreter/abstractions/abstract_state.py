from dataclasses import dataclass
from itertools import zip_longest
from typing import Union

from static_analysis.interpreter.abstractions.bool_set import BoolSet
from static_analysis.interpreter.abstractions.sign_set import SignSet

AbstractValue = Union[SignSet, BoolSet]

@dataclass
class AbstractState:
    stack: list[AbstractValue]
    locals: list[AbstractValue]
    done: str = None

    def __le__(self, other: 'AbstractState') -> bool:
        # Element-wise comparison for ordering
        stack_le = all(s1 <= s2 for s1, s2 in zip_longest(self.stack, other.stack, fillvalue=set()))
        locals_le = all(l1 <= l2 for l1, l2 in zip_longest(self.locals, other.locals, fillvalue=set()))
        return stack_le and locals_le
        
    def __and__(self, other: 'AbstractState') -> 'AbstractState':
        # Element-wise meet operation

        left_stack = other.stack
        right_stack = self.stack

        if len(self.stack) > len(other.stack):
            left_stack = self.stack
            right_stack = other.stack

        left_locals = other.locals
        right_locals = self.locals

        if len(self.locals) > len(other.locals):
            left_locals = self.locals
            right_locals = other.locals

        stack_meet = [s1 & s2 for s1, s2 in zip_longest(left_stack, right_stack, fillvalue=set())]
        locals_meet = [l1 & l2 for l1, l2 in zip_longest(left_locals, right_locals, fillvalue=set())]
        return AbstractState(stack=stack_meet, locals=locals_meet)
    
    def __or__(self, other: 'AbstractState') -> 'AbstractState':
        # Element-wise join operation
        left_stack = other.stack
        right_stack = self.stack

        if len(self.stack) > len(other.stack):
            left_stack = self.stack
            right_stack = other.stack

        left_locals = other.locals
        right_locals = self.locals

        if len(self.locals) > len(other.locals):
            left_locals = self.locals
            right_locals = other.locals

        stack_join = [s1 | s2 for s1, s2 in zip_longest(left_stack, right_stack, fillvalue=set())]
        locals_join = [l1 | l2 for l1, l2 in zip_longest(left_locals, right_locals, fillvalue=set())]
        return AbstractState(stack=stack_join, locals=locals_join)

    def copy(self):
        return AbstractState(
            stack=self.stack.copy(), 
            locals=self.locals.copy(),
        )
    
    def __hash__(self) -> int:
        return hash((tuple(self.stack), tuple(self.locals), self.done))
    
    def __eq__(self, other: 'AbstractState') -> bool:
        return self.stack == other.stack\
            and self.locals == other.locals\
            and self.done == other.done

    @staticmethod
    def bot():
        return AbstractState([], [])