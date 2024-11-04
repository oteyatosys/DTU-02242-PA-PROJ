from static_analysis.sign_set import SignSet, Sign
from hypothesis import given, assume
from hypothesis.strategies import sets, integers

BoolSet = set[bool]

class Arithmetic:
   
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
        return Arithmetic.lt(a, b) | Arithmetic.eq(a, b)

    @staticmethod
    def ge(a: Sign, b: Sign) -> BoolSet:
        return Arithmetic.gt(a, b) | Arithmetic.eq(a, b)

    @staticmethod
    def compare(opr, a: SignSet, b: SignSet) -> BoolSet:
        operations = {
            "eq": Arithmetic.eq,
            "ne": Arithmetic.ne,
            "lt": Arithmetic.lt,
            "gt": Arithmetic.gt,
            "le": Arithmetic.le,
            "ge": Arithmetic.ge
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
            "add": Arithmetic.add,
            "sub": Arithmetic.sub,
            "mul": Arithmetic.mul,
            "div": Arithmetic.div
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


@given(sets(integers()), sets(integers()))
def test_sign_add(xs, ys):
  assert (
    SignSet.abstract({x + y for x in xs for y in ys}) 
      <= Arithmetic.binary("add", SignSet.abstract(xs), SignSet.abstract(ys))
    )

@given(sets(integers()), sets(integers()))
def test_sign_sub(xs, ys):
    assert (
        SignSet.abstract({x - y for x in xs for y in ys}) 
            <= Arithmetic.binary("sub", SignSet.abstract(xs), SignSet.abstract(ys))
        )

@given(sets(integers()), sets(integers()))
def test_sign_mul(xs, ys):
    assert (
        SignSet.abstract({x * y for x in xs for y in ys}) 
            <= Arithmetic.binary("mul", SignSet.abstract(xs), SignSet.abstract(ys))
        )

@given(sets(integers()), sets(integers()))
def test_sign_div(xs, ys):
    assume(0 not in ys)
    assert (
        SignSet.abstract({x / y for x in xs for y in ys}) 
            <= Arithmetic.binary("div", SignSet.abstract(xs), SignSet.abstract(ys))
        )

@given(sets(integers()), sets(integers()))
def test_sign_eq(xs, ys):
    assert (
      {x == y for x in xs for y in ys} 
        <= Arithmetic.compare("eq", SignSet.abstract(xs), SignSet.abstract(ys))
    )

@given(sets(integers()), sets(integers()))
def test_sign_ne(xs, ys):
    assert (
      {x != y for x in xs for y in ys} 
        <= Arithmetic.compare("ne", SignSet.abstract(xs), SignSet.abstract(ys))
    )

@given(sets(integers()), sets(integers()))
def test_sign_lt(xs, ys):
    assert (
      {x < y for x in xs for y in ys} 
        <= Arithmetic.compare("lt", SignSet.abstract(xs), SignSet.abstract(ys))
    )

@given(sets(integers()), sets(integers()))
def test_sign_gt(xs, ys):
    assert (
      {x > y for x in xs for y in ys} 
        <= Arithmetic.compare("gt", SignSet.abstract(xs), SignSet.abstract(ys))
    )

@given(sets(integers()), sets(integers()))
def test_sign_le(xs, ys):
    assert (
      {x <= y for x in xs for y in ys} 
        <= Arithmetic.compare("le", SignSet.abstract(xs), SignSet.abstract(ys))
    )

@given(sets(integers()), sets(integers()))
def test_sign_ge(xs, ys):
    assert (
      {x >= y for x in xs for y in ys} 
        <= Arithmetic.compare("ge", SignSet.abstract(xs), SignSet.abstract(ys))
    )

test_sign_add()
test_sign_sub()
test_sign_mul()
test_sign_div()
test_sign_eq()
test_sign_ne()
test_sign_lt()
test_sign_gt()
test_sign_le()
test_sign_ge()