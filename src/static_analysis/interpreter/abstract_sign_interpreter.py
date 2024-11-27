from static_analysis.interpreter.abstractions import AbstractState, BoolSet, SignSet
from static_analysis.interpreter.arithmetic import BoolArithmetic, SignArithmetic
from static_analysis.interpreter.common import NextState, PC
from static_analysis.interpreter.abstract_interpreter import AbstractInterpreter
from reader import Program

class AbstractSignInterpreter(AbstractInterpreter):
    def __init__(self, program: Program):
        super().__init__(program)
        self.int_arithmetic = SignArithmetic()
        self.bool_arithmetic = BoolArithmetic()

    def join_states(self, old: AbstractState, new: AbstractState):
        return old | new

    def step_binary(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        right = new_state.stack.pop()
        left = new_state.stack.pop()

        arithmetic = self.get_arithmetic(left)

        try:
            result = arithmetic.binary(bc["operant"], left, right)
            new_state.stack.append(result)

            yield (pc.next(), NextState(new_state))
        except ZeroDivisionError:
            new_state.done = "zero division"
            self.errors.add("zero division")
            yield (-1, NextState(new_state))

            right -= SignSet({'0'})

            new_state = astate.copy()
            new_state.stack[-1] = right

            for res in self.step_binary(bc, pc, new_state):
                yield res

    def get_arithmetic(self, value):
        if isinstance(value, SignSet):
            return self.int_arithmetic
        elif isinstance(value, BoolSet):
            return self.bool_arithmetic
        else:
            raise NotImplementedError(f"can't handle {value!r}")
