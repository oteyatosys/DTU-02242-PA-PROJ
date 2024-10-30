from dataclasses import dataclass
from typing import Union
from static_analysis.sign_set import SignSet

AbstractValues = Union[SignSet, str]

@dataclass
class State:
    stack: list[AbstractValues]
    locals: list[AbstractValues]

    def copy(self):
        return State(
            stack=self.stack.copy(),
            locals=self.locals.copy()
        )

    @staticmethod
    def abstract(stack: list, locals: list):
        return State(
            stack=[SignSet.abstract(value) for value in stack],
            locals=[SignSet.abstract(value) for value in locals]
        )
    
    def __or__(self, other):
        if len(self.stack) != len(other.stack):
            raise ValueError("stacks must be of equal length")
        if len(self.locals) != len(other.locals):
            raise ValueError("locals must be of equal length")
        return State(
            stack=[x if x == y else x | y for x, y in zip(self.stack, other.stack)],
            locals=[x | y for x, y in zip(self.locals, other.locals)]
        )
    
    def __and__(self, other):
        if len(self.stack) != len(other.stack):
            raise ValueError("stacks must be of equal length")
        if len(self.locals) != len(other.locals):
            raise ValueError("locals must be of equal length")
        return State(
            stack=[x & y for x, y in zip(self.stack, other.stack)],
            locals=[x & y for x, y in zip(self.locals, other.locals)]
        )

    class Bot:
        def __contains__(self, _):
            return False

        def __le__(self, _):
            return True

        def __and__(self, _):
            return self

        def __or__(self, other):
            return other
