from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Set, Tuple
from static_analysis.interpreter.abstract_interpreter import PC, NextState, ReturnValue, Action
from static_analysis.interpreter.abstractions import AbstractState, BoolSet, Bot
from static_analysis.interpreter.abstractions.itval import Interval
from static_analysis.interpreter.arithmetic.arithmetic import Arithmetic
from reader import Program, MethodSignature
import logging as l

class ItAbstractInterpreter:
    def __init__(self, program: Program, arithmetic: Arithmetic, interesting_values: Set[int]):
        self.program = program
        self.arithmetic = arithmetic
        self.generated = 0
        self.final = set()
        self.errors = set()
        self.interesting_values: Set[int] = interesting_values

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
                new_state = old.widening(self.interesting_values, next_state)

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

    def step(self, pc: PC, astate: AbstractState) -> Iterable[Tuple[PC, Action]]:
        bc = self.program.method(pc.signature).bytecode[pc.offset]

        l.debug(f"Running: {bc['opr']}")

        for (pc_, s_) in self.lookup(f"step_{bc['opr']}")(bc, pc, astate):
            pc_: PC
            s_: Action

            if pc_ == -1:
                self.final.add(s_)
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
        new_state = astate.copy()

        right = new_state.stack.pop()
        left = new_state.stack.pop()

        try:
            result = self.arithmetic.binary(bc["operant"], left, right)
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

        error: object = next(iter(new_state.stack.pop()))

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

        new_state.stack.append(self.arithmetic.negate(left))

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
                Interval.abstract({value})
            )
        elif type == "boolean":
            new_state.stack.append(
                BoolSet.abstract({value})
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

        if isinstance(left, BoolSet):
            left = Interval.from_boolset(left)

        for b in self.arithmetic.compare(bc["condition"], left, Interval(0, 0)):
            l.debug(f"Comparing {left} to 0 {bc['condition']}: {b}")
            if b:
                yield (pc.jump(bc["target"]), NextState(astate.copy()))
            else:
                yield (pc.next(), NextState(astate.copy()))
    
    def step_if(self, bc: list, pc: PC, astate: AbstractState):
        right = astate.stack.pop()
        left = astate.stack.pop()

        for b in self.arithmetic.compare(bc["condition"], left, right):
            if b:
                yield (pc.jump(bc["target"]), NextState(astate.copy()))
            else:
                yield (pc.next(), NextState(astate.copy()))

    def step_new(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        if bc["class"] == "java/lang/AssertionError":
            new_state.stack.append(frozenset(["assertion error"]))
        else:
            raise NotImplementedError(f"can't handle {bc!r}")

        yield (pc.next(), NextState(new_state))

    def step_get(self, bc: list, pc: PC, astate: AbstractState):
        new_state = astate.copy()

        new_state.stack.append(BoolSet(False))

        yield (pc.next(), NextState(new_state))


