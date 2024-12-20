from typing import Dict, Iterable, List, Set, Tuple
from static_analysis.interpreter.common import PC, NextState, ReturnValue, Action
from static_analysis.interpreter.abstractions import AbstractState, BoolSet, Bot, RefSet
from reader import Program, MethodSignature
import logging as l

class AbstractInterpreter:
    def __init__(self, program: Program):
        self.program = program
        self.generated = 0
        self.final = set()
        self.errors = set()
        
        # Must be set up by the subclass
        self.int_arithmetic = None
        self.bool_arithmetic = None

    def analyse(self, pc: PC, initial_state: AbstractState) -> Dict[MethodSignature, Set[int]]:
        states: Dict[PC, AbstractState] = {pc: initial_state}
        needs_work: List[PC] = [pc]

        while needs_work:
            curr_idx = needs_work.pop()

            for (next_pc, next_action) in self.step(curr_idx, states[curr_idx].copy()):
                self.generated += 1

                next_state = None
 
                match next_action:
                    case NextState(astate):
                        next_state = astate
                    case ReturnValue(value, param_count):
                        next_state = states.get(next_pc.prev()).copy()

                        if param_count > 0:
                            next_state.stack = next_state.stack[:-param_count]
                        
                        next_state.stack.append(value)

 
                old = states.get(next_pc, Bot())
                new_state = self.join_states(old, next_state)

                if old != new_state:
                    states[next_pc] = new_state
                    needs_work.append(next_pc)
                    l.debug(f"New state at {next_pc}")
                    l.debug(f"new: {new_state}")

        l.debug(f"Generated {self.generated} states")

        touched = dict()
        for pc in states.keys():
            pcs = touched.get(pc.signature, set())
            pcs.add(pc.offset)
            touched[pc.signature] = pcs
        
        return touched

    def join_states(self, old: AbstractState, new: AbstractState):
        raise NotImplementedError("join_states")

    def step(self, pc: PC, astate: AbstractState) -> Iterable[Tuple[PC, Action]]:
        bc = self.program.method(pc.signature).bytecode[pc.offset]

        l.debug(f"Running: {bc['opr']}")

        for (pc_, s_) in self.lookup(f"step_{bc['opr']}")(bc, pc, astate):
            pc_: PC
            s_: Action

            if pc_ == -1:
                l.debug(f"Final state: {repr(s_)}")
                # self.final.add(s_)
            else:
                yield (pc_, s_)

    def lookup(self, name: str):
        if fn := getattr(self, name, None):
            return fn
        else:
            raise NotImplementedError(f"can't handle {name!r}")

    def step_goto(self, bc: list, pc: PC, astate: AbstractState):
        yield (pc.jump(bc["target"]), NextState(astate.copy()))

    def step_binary(self, bc: list, pc: PC, astate: AbstractState):
        raise NotImplementedError("step_binary")

    def step_load(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        index: int = bc["index"]

        new_state.stack.append(new_state.locals[index])

        yield (pc.next(), NextState(new_state))


    def step_store(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        index: int = bc["index"]

        new_state.locals[index] = new_state.stack.pop()

        yield (pc.next(), NextState(new_state))
        

    def step_throw(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        error: object = new_state.stack.pop()

        self.errors.add(error)

        new_state.done = error

        yield (-1, NextState(new_state))

    def step_invoke(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()
        access: str = bc["access"]

        if access == "special":
            # Just pass, as method invocation on objects is not supported
            yield (pc.next(), NextState(astate))
        elif access == "static":
            # Extract arguments from the stack
            signature = MethodSignature.from_bytecode(bc["method"])

            args = dict(
                enumerate(astate.stack[-len(signature.parameters):])
            ) if len(signature.parameters) > 0 else dict()

            new_state = AbstractState(
                [{pc.next()}],
                args
            )

            yield(PC(signature, 0), NextState(new_state))
        else:
            raise NotImplementedError(f"can't handle {access!r}")

    def step_negate(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        left = new_state.stack.pop()
        arithmetic = self.get_arithmetic(left)

        new_state.stack.append(arithmetic.negate(left))

        yield (pc.next(), NextState(new_state))

    def step_dup(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        count: int = bc["words"]

        dup = new_state.stack[-count:]

        new_state.stack.extend(dup)

        yield (pc.next(), NextState(new_state))

    def step_push(self, b: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()
        type = b["value"]["type"]
        value = b["value"]["value"]

        if type == "integer":
            new_state.stack.append(
                self.int_arithmetic.abstract({value})
            )
        elif type == "boolean":
            new_state.stack.append(
                self.bool_arithmetic.abstract({value})
            )
        else:
            new_state.stack.append(value)
        
        yield (pc.next(), NextState(new_state))

    def step_return(self, b: list, pc: PC, astate: AbstractState) -> Iterable[Tuple[PC, ReturnValue]]:
        new_state = astate.copy()

        param_count = len(pc.signature.parameters)

        if b["type"] is not None:
            return_value = new_state.stack.pop()
            try:
                targets: Set[PC] = new_state.stack.pop()
            except IndexError:
                yield (-1, ReturnValue(return_value, param_count))
                return

            for target in targets:
                yield (target, ReturnValue(return_value, param_count))
        
        else:
            yield (-1, ReturnValue(None, param_count))
            
    def step_ifz(self, bc: list, pc: PC, astate: AbstractState):
        left = astate.stack.pop()
        arithmetic = self.get_arithmetic(left)
        right = arithmetic.from_int(0)

        for b in arithmetic.compare(bc["condition"], left, right):
            l.debug(f"Comparing {left} to {right} {bc['condition']}: {b}")
            if b:
                yield (pc.jump(bc["target"]), NextState(astate.copy()))
            else:
                yield (pc.next(), NextState(astate.copy()))
    
    def step_if(self, bc: list, pc: PC, astate: AbstractState):
        right = astate.stack.pop()
        left = astate.stack.pop()

        arithmetic = self.get_arithmetic(left)

        for b in arithmetic.compare(bc["condition"], left, right):
            l.debug(f"Comparing {left} to {right} {bc['condition']}: {b}")
            if b:
                yield (pc.jump(bc["target"]), NextState(astate.copy()))
            else:
                yield (pc.next(), NextState(astate.copy()))

    def step_new(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        match bc["class"]:
            case "java/lang/AssertionError" | "java/lang/RuntimeException":
                new_state.stack.append(RefSet({bc["class"]}))
            case _:
                raise NotImplementedError(f"can't handle {bc!r}")

        yield (pc.next(), NextState(new_state))

    def step_get(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        new_state.stack.append(BoolSet(False))

        yield (pc.next(), NextState(new_state))

    def step_incr(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        index = bc["index"]
        
        left = new_state.locals[index]
        arithmetic = self.get_arithmetic(left)
        right = arithmetic.from_int(bc["amount"])

        new_state.locals[index] = arithmetic.binary("add", left, right)

        yield (pc.next(), NextState(new_state))

    def get_arithmetic(self, value):
        raise NotImplementedError("get_arithmetic")



