from typing import Set
from static_analysis.interpreter.common import PC, NextState
from static_analysis.interpreter.abstract_interpreter import AbstractInterpreter
from static_analysis.interpreter.abstractions import AbstractState, BoolSet, Interval
from static_analysis.interpreter.arithmetic import BoolArithmetic, IntervalArithmetic
from reader import Program
from syntactic_analysis.scanner import get_int_literals

class AbstractIntervalInterpreter(AbstractInterpreter):
    def __init__(self, program: Program):
        super().__init__(program)
        self.int_arithmetic = IntervalArithmetic()
        self.bool_arithmetic = BoolArithmetic()
        self.interesting_values: Set[int] = get_int_literals(program)

    def join_states(self, old: AbstractState, new: AbstractState):
        return old.widening(self.interesting_values, new)

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

            right1 = right and Interval(float("-inf"),-1)
            right2 = right and Interval(1,float("inf"))
            if right1 != Interval.bot() :
                new_state1 = astate.copy()
                new_state1.stack[-1] = right1
                for res in self.step_binary(bc, pc, new_state1):
                    yield res 
                    
            if right2 != Interval.bot() :
                new_state2 = astate.copy()          
                new_state2.stack[-1] = right2
                for res in self.step_binary(bc, pc, new_state2):
                    yield res

    def get_arithmetic(self, value):
        if isinstance(value, Interval):
            return self.int_arithmetic
        elif isinstance(value, BoolSet):
            return self.bool_arithmetic
        else:
            raise NotImplementedError(f"can't handle {value!r}")

