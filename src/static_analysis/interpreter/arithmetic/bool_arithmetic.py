from dataclasses import dataclass
import itertools
from static_analysis.interpreter.abstractions.bool_set import BoolSet
from static_analysis.interpreter.arithmetic.arithmetic import Arithmetic

@dataclass
class BoolArithmetic(Arithmetic[BoolSet]):

    def abstract(self, value) -> BoolSet:
        return BoolSet.abstract(value)
    
    def from_int(self, i: int) -> BoolSet:
        return BoolSet(i != 0)
    
    def compare(self, opr: str, a: BoolSet, b: BoolSet) -> BoolSet:
        combinations = itertools.product(a, b)

        result_set: BoolSet = BoolSet()

        for (a, b) in combinations:
            if opr == "eq":
                result_set |= BoolSet( a == b )
            elif opr == "ne":
                result_set |= BoolSet( a != b )
            elif opr == "lt":
                result_set |= BoolSet( a < b )
            elif opr == "le":
                result_set |= BoolSet( a <= b )
            elif opr == "gt":
                result_set |= BoolSet( a > b )
            elif opr == "ge":
                result_set |= BoolSet( a >= b )
            else:
                raise NotImplementedError(f"can't handle {opr!r}")

        return result_set
