from interpreter.static.abstractions.sign_set import SignSet, Sign
from hypothesis import given, assume
from hypothesis.strategies import sets, integers

BoolSet = set[bool]

class SignArithmetic:
   
    @staticmethod
    def eq(a: Sign, b: Sign) -> BoolSet:
        match (a, b):
            case ("+", "+") | ("-", "-"): return {True, False}
            case ("0", "0"): return {True}
            case (_, _): return {False}
    
    @staticmethod
    def ne(a: Sign, b: Sign) -> BoolSet:
        match (a, b):
            case ("+", "+") | ("-", "-"): return {True, False}
            case ("0", "0"): return {False}
            case (_, _): return {True}

    @staticmethod
    def lt(a: Sign, b: Sign) -> BoolSet:
        match (a, b):
            case ("+", "+"): return {True, False}
            case ("+", _): return {False}
            case ("0", "+"): return {True}
            case ("0", _): return {False}
            case ("-", "-"): return {True, False}
            case ("-", _): return {True}

    @staticmethod
    def gt(a: Sign, b: Sign) -> BoolSet:
        match (a, b):
            case ("+", "+"): return {True, False}
            case ("+", _): return {True}
            case ("0", "+" | "0"): return {False}
            case ("0", "-"): return {True}
            case ("-", "-"): return {True, False}
            case ("-", _): return {False}

    @staticmethod
    def le(a: Sign, b: Sign) -> BoolSet:
        return SignArithmetic.lt(a, b) | SignArithmetic.eq(a, b)

    @staticmethod
    def ge(a: Sign, b: Sign) -> BoolSet:
        return SignArithmetic.gt(a, b) | SignArithmetic.eq(a, b)

    @staticmethod
    def compare(opr, a: SignSet, b: SignSet) -> BoolSet:
        operations = {
            "eq": SignArithmetic.eq,
            "ne": SignArithmetic.ne,
            "lt": SignArithmetic.lt,
            "gt": SignArithmetic.gt,
            "le": SignArithmetic.le,
            "ge": SignArithmetic.ge
        }
        if opr in operations:
            func = operations[opr]
            out = set()
            for x in a.signs:
                for y in b.signs:
                    out = out.union(func(x, y))
            return out
        else:
            raise ValueError(f"Unknown comparison operator")

    @staticmethod
    def add(a: Sign, b: Sign) -> set[Sign]:
        match (a, b):
            case ("+", "+"): return {"+"}
            case ("+", "-"): return {"+", "-", "0"}
            case ("-", "+"): return {"+", "-", "0"}
            case ("-", "-"): return {"-"}
            case (_, "0"): return {a}
            case ("0", _): return {b}
    
    @staticmethod
    def sub(a: Sign, b: Sign) -> set[Sign]:
        match (a, b):
            case ("+", "+"): return {"+", "0", "-"}
            case ("+", "-"): return {"+"}
            case ("-", "+"): return {"-"}
            case ("-", "-"): return {"-", "0", "+"}
            case ("0", "-"): return {"+"}
            case ("0", "+"): return {"-"}
            case (_, "0"): return {a}

    @staticmethod
    def mul(a: Sign, b: Sign) -> set[Sign]:
        match (a, b):
            case ("+", "+"): return {"+"}
            case ("+", "-"): return {"-"}
            case ("-", "+"): return {"-"}
            case ("-", "-"): return {"+"}
            case (_, "0"): return {"0"}
            case ("0", _): return {"0"}

    @staticmethod
    def div(a: Sign, b: Sign) -> set[Sign]:
        match (a, b):
            case ("+", "+"): return {"+", "0"}
            case ("+", "-"): return {"-", "0"}
            case ("-", "+"): return {"-", "0"}
            case ("-", "-"): return {"+", "0"}
            case (_, "0"): raise ZeroDivisionError
            case ("0", _): return {"0"}

    @staticmethod
    def binary(opr: str, a: SignSet, b: SignSet) -> SignSet:
        operations = {
            "add": SignArithmetic.add,
            "sub": SignArithmetic.sub,
            "mul": SignArithmetic.mul,
            "div": SignArithmetic.div
        }
        if opr in operations:
            func = operations[opr]
            out = SignSet(set())
            for x in a.signs:
                for y in b.signs:
                    out |= SignSet(func(x, y))
            return out

        else:
            raise ValueError(f"Unknown binary operator {opr}")