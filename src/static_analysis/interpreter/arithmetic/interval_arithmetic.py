from dataclasses import dataclass
from static_analysis.interpreter.abstractions.bool_set import BoolSet
from static_analysis.interpreter.abstractions.interval import Interval
from static_analysis.interpreter.arithmetic.arithmetic import Arithmetic

@dataclass
class IntervalArithmetic(Arithmetic[Interval]):
    
    @staticmethod
    def abstract(value) -> Interval:
        return Interval.abstract(value)

    @staticmethod
    def from_int(a: int) -> Interval:
        return Interval(a, a)

    @staticmethod
    def binary(opr: str, a: Interval, b: Interval) -> Interval:

        if opr == "add":
            return Interval(a.lb + b.lb, a.ub + b.ub)

        elif opr == "sub":
            return Interval(a.lb - b.ub, a.ub - b.lb)

        elif opr == "mul":
            lower_bound = min(a.lb * b.lb, a.lb * b.ub, a.ub * b.lb, a.ub * b.ub)
            upper_bound = max(a.lb * b.lb, a.lb * b.ub, a.ub * b.lb, a.ub * b.ub)
            return Interval(lower_bound, upper_bound)
        elif opr == "div":
            if 0 in b :
                raise ZeroDivisionError
            else :
                lower_bound = min(a.lb // b.lb, a.lb // b.ub, a.ub // b.lb, a.ub // b.ub)
                upper_bound = max(a.lb // b.lb, a.lb // b.ub, a.ub // b.lb, a.ub // b.ub)
                return Interval(lower_bound, upper_bound)
        else:
            raise NotImplementedError(f"can't handle {opr!r}")

    @staticmethod
    def compare(opr: str, a: Interval, b: Interval) -> BoolSet:
        if opr == "eq":
            result_set: BoolSet = BoolSet()
            intersection = a & b
            if (a.lb == b.lb == a.ub == b.ub):
                result_set |= BoolSet(True)
            elif (intersection.lb == float("inf") and intersection.ub == float("-inf")):
                result_set |= BoolSet(False)
            else:
                result_set |= BoolSet(True, False)

            return result_set

        elif opr == "ne":
            result_set: BoolSet = BoolSet()
            intersection = a & b
            if (a.lb == b.lb == a.ub == b.ub):
                result_set |= BoolSet(False)
            elif (intersection.lb == float("inf") and intersection.ub == float("-inf")):
                result_set |= BoolSet(True)
            else:
                result_set |= BoolSet(True, False)

            return result_set
        
        elif opr == "gt":
            result_set: BoolSet = BoolSet()
            if a.lb <= b.ub :
                result_set |= BoolSet(False)
            else : result_set |= BoolSet(True)
            if a.ub <= b.lb :
                result_set |= BoolSet(False)
            else : result_set |= BoolSet(True)
            return result_set
        
        elif opr == "ge":
            result_set: BoolSet = BoolSet()
            if a.lb < b.ub :
                result_set |= BoolSet(False)
            else : result_set |= BoolSet(True)

            if a.ub < b.lb :
                result_set |= BoolSet(False)
            else : result_set |= BoolSet(True)

            return result_set
        
        elif opr == "le":
            result_set: BoolSet = BoolSet()
            if a.lb > b.ub :
                result_set |= BoolSet(False)
            else : result_set |= BoolSet(True)

            if a.ub > b.lb :
                result_set |= BoolSet(False)
            else : result_set |= BoolSet(True)

            return result_set

        else:
            raise NotImplementedError(f"can't handle {opr!r}")
        
    def negate(self, a: Interval) -> Interval:
        return Interval(-a.ub, -a.lb)
