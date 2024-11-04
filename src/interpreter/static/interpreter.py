from dataclasses import dataclass
from interpreter.arithmetic.sign_arithmetic import SignArithmetic
from interpreter.static.abstractions.sign_set import SignSet
from interpreter.static.state import State

PC = int

@dataclass
class Interpreter:
    bytecode : dict
    states : dict[PC, State]
    final : set[str]
    arithmetic : SignArithmetic

    def step(self):
        next_states = self.states.copy()
        for pc, astate in self.states.items():
            instr = self.bytecode[pc]
            if fn := getattr(self, f"step_{instr['opr']}"):
                print("running: ", instr['opr'])
                for (pc_, s_) in fn(instr, pc, astate.copy()):
                    # if the pc_ is -1 we are "done", and s_ is the end string
                    if pc_ == -1:
                        self.final.add(s_)
                    else:
                        # merge the new state with the current state or bottom
                        next_states[pc_] = next_states.get(pc_, State.Bot()) | s_
            else:
                raise NotImplementedError(f"can't handle {instr['opr']!r}")
            self.states = next_states

    def step_get(self, _bc, pc, astate):
        if _bc["field"]["name"] != "$assertionsDisabled":
            raise NotImplementedError(f"can't handle {_bc['field']['name']!r}")
        
        astate.stack.append(SignSet({"0"}))
        yield (pc + 1, astate.copy())

    # Stepping functions are now generators that can generate different 
    # states depending on the abstract state.
    def step_ifz(self, bc, pc, astate):
        # depending on the defintion of the abstract_state 

        aval = astate.stack.pop()
        # Note that the abstract value might both compare and not compare to 0
        for b in self.arithmetic.compare(bc["condition"], aval, SignSet({'0'})):
            if b:
                yield (bc["target"], astate.copy())
            else:
                yield (pc + 1, astate.copy())

    def step_if(self, bc, pc, astate):
        right = astate.stack.pop()
        left = astate.stack.pop()
        for b in self.arithmetic.compare(bc["condition"], left, right):
            if b:
                yield (bc["target"], astate.copy())
            else:
                yield (pc + 1, astate.copy())

    def step_load(self, bc, pc, astate):
        astate.stack.append(astate.locals[bc["index"]])
        yield (pc + 1, astate.copy())

    def step_new(self, bc, pc, astate):
        if bc["class"] == "java/lang/AssertionError":
            # We expect assertion error to be thrown
            # The right way might be to set it on the stack

            # yield (-1, "assertion_error")
            astate.stack.append("assertion error")
            yield (pc + 1, astate.copy())
        else:
            raise NotImplementedError(f"calling new for anything else than AssertionError")

    def step_push(self, bc, pc, astate):
        if bc["value"] is None:
            raise NotImplementedError("trying to push None!!")
        else:
            abstract_value = SignSet.abstract({bc["value"]["value"]})
            astate.stack.append(abstract_value)
        yield (pc + 1, astate.copy())

    def step_return(self, bc, pc, astate):
        # TODO implement method stack
        if bc["type"] is not None: astate.stack.pop()
        yield (-1, "ok")

    def step_binary(self, bc, pc, astate):
        right = astate.stack.pop()
        left = astate.stack.pop()
        
        if SignSet({'0'}) <= right:
            yield (-1, "divide by zero")
            right &= SignSet({"-","+"})

        astate.stack.append(self.arithmetic.binary(bc["operant"], left, right))
        yield (pc + 1, astate.copy())

    def step_dup(self, bc, pc, astate):
        count: int = bc["words"]
        astate.stack.extend(astate.stack[-count:])
        yield (pc + 1, astate.copy())

    def step_invoke(self, bc, pc, astate):
        if bc["access"] == "special" and bc["method"]['name'] == '<init>' and bc["method"]["ref"]["name"] == "java/lang/AssertionError":
            # Continue as if nothing happened
            yield (pc + 1, astate.copy())
        else:
            raise NotImplementedError("invoke not implemented")

    def step_throw(self, bc, pc, astate):
        value = astate.stack.pop()
        yield (-1, value)
