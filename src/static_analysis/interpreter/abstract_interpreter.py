from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple

import sys

from static_analysis.interpreter.abstractions.abstract_state import AbstractState
from static_analysis.interpreter.abstractions.bool_set import BoolSet
from static_analysis.interpreter.abstractions.sign_set import SignSet
from static_analysis.interpreter.arithmetic.arithmetic import Arithmetic
from static_analysis.interpreter.arithmetic.sign_arithmetic import SignArithmetic
from static_analysis.method_id import MethodId
from static_analysis.program import Program
from jpamb_utils import JvmType

PC = int

@dataclass
class AbstractInterpreter:
    bytecode : dict[int, list]
    final : set[str]
    arithmetic : Arithmetic
    seen: Set[AbstractState] = field(default_factory=set)
    generated: int = 0

    def interpret(self):
        timeout: int = 10000
        for i in range(timeout):
            self.step()
            
        print(f"Generated {self.generated} states")

    def analyse(self, initial: Tuple[PC, AbstractState]):
        states: Dict[PC, AbstractState] = {initial[0]: initial[1]}
        needs_work: List[int] = [initial[0]]

        while needs_work:
            curr_idx = needs_work.pop()

            for pc, astate in self.step(curr_idx, states[curr_idx]):
                self.generated += 1

                old = states.get(pc, AbstractState.bot())
                
                states[pc] = old | astate

                if old != states[pc]:
                    needs_work.append(pc)
                    print(f"New state at {pc}")

        print(f"Generated {self.generated} states")


    def step(self, pc: int, astate: AbstractState):
        bc = self.bytecode[pc]
        print(f"Running: ${bc['opr']}")

        for (pc_, s_) in self.lookup(f"step_{bc['opr']}")(bc, pc, astate):

            if pc_ == -1:
                self.final.add(s_.done)
            else:
                yield (pc_, s_)

    def lookup(self, name: str):
        if fn := getattr(self, name, None):
            return fn
        else:
            raise NotImplementedError(f"can't handle {name!r}")

    def step_goto(self, bc: list, pc: int, astate: AbstractState):
        yield (bc["target"], astate.copy())

    def step_binary(self, bc: list, pc: int, astate: AbstractState):
        new_state = astate.copy()

        right = new_state.stack.pop()
        left = new_state.stack.pop()

        try:
            result = self.arithmetic.binary(bc["operant"], left, right)
            new_state.stack.append(result)

            yield (pc + 1, new_state)
        except ZeroDivisionError:
            new_state.done = "zero division"
            yield (-1, new_state)

            right -= SignSet({'0'})

            new_state = astate.copy()
            new_state.stack[-1] = right

            for res in self.step_binary(bc, pc, new_state):
                yield res

    def step_load(self, bc: list, pc: int, astate: AbstractState):
        new_state = astate.copy()

        index: int = bc["index"]

        new_state.stack.append(new_state.locals[index])

        yield (pc + 1, new_state)

    def step_throw(self, bc: list, pc: int, astate: AbstractState):
        new_state = astate.copy()

        error: object = next(iter(new_state.stack.pop()))

        new_state.done = error

        yield (-1, new_state)

    def step_invoke(self, bc: list, pc: int, astate: AbstractState):
        access: str = bc["access"]

        if access == "special":
            # Just pass, as method invocation on objects is not supported

            yield (pc + 1, astate)
        else:
            raise NotImplemented(f"can't handle {bc!r}")

    def step_dup(self, bc: list, pc: int, astate: AbstractState):
        new_state = astate.copy()

        count: int = bc["words"]

        dup = new_state.stack[-count:]

        new_state.stack.extend(dup)

        yield (pc + 1, new_state)

    def step_push(self, b: list, pc: int, astate: AbstractState):
        new_state = astate.copy()

        new_state.stack.append(
            SignSet.abstract({b["value"]["value"]})
        )

        yield (pc + 1, new_state)

    def step_return(self, b: list, pc: int, astate: AbstractState):
        new_state = astate.copy()

        new_state.done = "ok"

        yield (-1, new_state)

    # Stepping functions are now generators that can generate different 
    # states depending on the abstract state.
    def step_ifz(self, bc: list, pc: int, astate: AbstractState):
        # depending on the defintion of the abstract_state 
        left = astate.stack.pop()
        # Note that the abstract value might both compare and not compare to 0
        for b in self.arithmetic.compare(bc["condition"], left, SignSet({'0'})):
            if b:
                yield (bc["target"], astate.copy())
            else:
                yield (pc + 1, astate.copy())

    def step_new(self, bc: list, pc: int, astate: AbstractState):
        new_state = astate.copy()

        if bc["class"] == "java/lang/AssertionError":
            new_state.stack.append(frozenset(["assertion error"]))
        else:
            raise NotImplementedError(f"can't handle {bc!r}")

        yield (pc + 1, new_state)

    def step_get(self, bc: list, pc: int, astate: AbstractState):
        new_state = astate.copy()

        new_state.stack.append(BoolSet(False))

        yield (pc + 1, new_state)


def generate_arguments(params: list[JvmType]):
    for param in params:
        if param == "int":
            yield SignSet.top()
        elif param == "boolean":
            yield BoolSet.top()
        else:
            raise NotImplementedError(f"can't handle {param!r}")


if __name__ == "__main__":
    program_path = Path("data", "decompiled")

    program: Program = Program.parse_program(program_path)

    entry_point = MethodId.parse(sys.argv[1])
    inputs = list(generate_arguments(entry_point.params))

    initial_state = AbstractState([], inputs)
    print(f"Initial state: {initial_state}")

    interpreter = AbstractInterpreter(
        bytecode=program.lookup(entry_point),
        final=set(),
        arithmetic=SignArithmetic()
    )

    interpreter.analyse((0, initial_state))

    print(f"End states: {interpreter.final}")