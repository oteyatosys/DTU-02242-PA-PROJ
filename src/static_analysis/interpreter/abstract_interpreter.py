from dataclasses import dataclass
from typing import Dict, List, Tuple
from static_analysis.interpreter.abstractions import AbstractState, BoolSet, SignSet, Bot
from static_analysis.interpreter.arithmetic.arithmetic import Arithmetic
from reader import Program, MethodSignature
from jpamb_utils import JvmType

@dataclass(frozen=True)
class PC:
    signature: MethodSignature
    offset: int

    def __add__(self, i: int):
        return PC(self.signature, self.offset + i)
    
    def next(self) -> 'PC':
        return self + 1
    
    def jump(self, i: int) -> 'PC':
        return PC(self.signature, i)
    
    def __lt__(self, other: 'PC') -> bool:
        return self.signature < other.signature or self.offset < other.offset


class AbstractInterpreter:
    def __init__(self, program: Program, arithmetic: Arithmetic):
        self.program = program
        self.arithmetic = arithmetic
        self.generated = 0
        self.final = set()
        self.pcs = set()

    def analyse(self, pc: PC, initial_state: AbstractState):
        states: Dict[PC, AbstractState] = {pc: initial_state}
        needs_work: List[PC] = [pc]

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


    def step(self, pc: PC, astate: AbstractState):
        bc = self.program.method(pc.signature).bytecode[pc.offset]

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

    def step_goto(self, bc: list, pc: PC, astate: AbstractState):
        yield (pc.jump(bc["target"]), astate.copy())

    def step_binary(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        right = new_state.stack.pop()
        left = new_state.stack.pop()

        try:
            result = self.arithmetic.binary(bc["operant"], left, right)
            new_state.stack.append(result)

            yield (pc.next(), new_state)
        except ZeroDivisionError:
            new_state.done = "zero division"
            yield (-1, new_state)

            right -= SignSet({'0'})

            new_state = astate.copy()
            new_state.stack[-1] = right

            for res in self.step_binary(bc, pc, new_state):
                yield res

    def step_load(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        index: int = bc["index"]

        new_state.stack.append(new_state.locals[index])

        yield (pc.next(), new_state)

    def step_throw(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        error: object = next(iter(new_state.stack.pop()))

        new_state.done = error

        yield (-1, new_state)

    def step_invoke(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()
        access: str = bc["access"]

        if access == "special":
            # Just pass, as method invocation on objects is not supported
            yield (pc.next(), astate)
        elif access == "static":
            # Extract arguments from the stack
            args = [new_state.stack.pop() for _ in bc["method"]["args"]]

            print(f"TODO: Spawn new abstract interpreter and collect return values")

            # Append the retunr value to the stack
            new_state.stack.append(SignSet.top())

            yield (pc.next(), new_state)
        else:
            raise NotImplemented(f"can't handle {bc!r}")

    def step_dup(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        count: int = bc["words"]

        dup = new_state.stack[-count:]

        new_state.stack.extend(dup)

        yield (pc.next(), new_state)

    def step_push(self, b: list, pc: PC, astate: AbstractState):
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
        
        yield (pc.next(), new_state)

    def step_return(self, b: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        print(f"TODO: Store return value in new_state.done")
        new_state.done = "ok"

        yield (-1, new_state)

    # Stepping functions are now generators that can generate different 
    # states depending on the abstract state.
    def step_ifz(self, bc: list, pc: PC, astate: AbstractState):
        # depending on the defintion of the abstract_state 
        left = astate.stack.pop()
        # Note that the abstract value might both compare and not compare to 0
        for b in self.arithmetic.compare(bc["condition"], left, SignSet({'0'})):
            if b:
                yield (pc.jump(bc["target"]), astate.copy())
            else:
                yield (pc.next(), astate.copy())
    
    def step_if(self, bc: list, pc: PC, astate: AbstractState):
        right = astate.stack.pop()
        left = astate.stack.pop()

        for b in self.arithmetic.compare(bc["condition"], left, right):
            if b:
                yield (pc.jump(bc["target"]), astate.copy())
            else:
                yield (pc.next(), astate.copy())

    def step_new(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        if bc["class"] == "java/lang/AssertionError":
            new_state.stack.append(frozenset(["assertion error"]))
        else:
            raise NotImplementedError(f"can't handle {bc!r}")

        yield (pc.next(), new_state)

    def step_get(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        new_state.stack.append(BoolSet(False))

        yield (pc.next(), new_state)


def generate_arguments(params: list[JvmType]):
    for param in params:
        if param == "int":
            yield SignSet.top()
        elif param == "boolean":
            yield BoolSet.top()
        else:
            raise NotImplementedError(f"can't handle {param!r}")


