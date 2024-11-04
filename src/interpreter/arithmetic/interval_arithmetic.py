from dataclasses import dataclass
from interpreter.static.abstractions.itval import Interval
@dataclass
class IntervalArithmetic:
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
    def compare(opr: str, a: Interval, b: Interval) -> bool:
        if opr == "eq":
            return (a.lb == b.lb and a.ub == b.ub)
        elif opr == "ne":
            return not(a.lb == b.lb and a.ub == b.ub)
        else:
            raise NotImplementedError(f"can't handle {opr!r}")