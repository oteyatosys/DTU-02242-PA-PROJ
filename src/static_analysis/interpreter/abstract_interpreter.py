from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from static_analysis.interpreter.abstractions import AbstractState, BoolSet, SignSet, Bot
from static_analysis.interpreter.arithmetic.arithmetic import Arithmetic
from jpamb_utils import JvmType

PC = int

@dataclass
class AbstractInterpreter:
    bytecode : dict[int, list]
    arithmetic : Arithmetic
    generated: int = 0
    final : set[str] = field(default_factory=set)
    pcs : set[int] = field(default_factory=set)

    def analyse(self, initial: Tuple[PC, AbstractState]):
        states: Dict[PC, AbstractState] = {initial[0]: initial[1]}
        needs_work: List[int] = [initial[0]]

        while needs_work:
            curr_idx = needs_work.pop()

            for pc, astate in self.step(curr_idx, states[curr_idx]):
                self.generated += 1

                old = states.get(pc, Bot())
                
                states[pc] = old | astate

                if old != states[pc]:
                    needs_work.append(pc)
                    print(f"New state at {pc}")

        print(f"Generated {self.generated} states")
        self.pcs.update(states.keys())
        print(f"Final states: {sorted(states.keys())}")


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
        elif access == "static":
            # TODO: Implement static method invocation
            print(f"TODO: Spawn new abstract interpreter and collect return values")
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
        type = b["value"]["type"]
        value = b["value"]["value"]

        if type == "integer":
            new_state.stack.append(
                SignSet.abstract({value})
            )
        elif type == "boolean":
            new_state.stack.append(
                BoolSet.abstract({value})
            )
        else:
            new_state.stack.append(value)
        
        yield (pc + 1, new_state)

    def step_return(self, b: list, pc: int, astate: AbstractState):
        new_state = astate.copy()

        print(f"TODO: Store return value in new_state.done")
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


