from dataclasses import dataclass
import itertools
from typing import Set, Tuple
from static_analysis.interpreter.abstractions.bool_set import BoolSet
from static_analysis.interpreter.abstractions.sign_set import SignSet, Sign
from static_analysis.interpreter.arithmetic.arithmetic import Arithmetic

@dataclass
class SignArithmetic(Arithmetic[SignSet]):
    _order: Tuple[Sign] = ("-", "0", "+")

    def abstract(self, value) -> SignSet:
        return SignSet.abstract(value)

    def from_int(self, i: int) -> SignSet:
        return self.abstract({i})

    def binary(self, opr: str, left: SignSet, right: SignSet) -> SignSet:
        combinations = itertools.product(left, right)

        result_set: SignSet = SignSet.bot()

        for (left, right) in combinations:
            if opr == "add":
                result_set |= self._add(left, right)

            elif opr == "sub":
                result_set |= self._sub(left, right)

            elif opr == "mul":
                result_set |= self._mul(left, right)

            elif opr == "div":
                result_set |= self._div(left, right)
            
            elif opr == "rem":
                result_set |= self._div(left, right)

            else:
                raise NotImplementedError(f"can't handle {opr!r}")
            
        return SignSet(result_set)

    def negate(self, a: SignSet) -> SignSet:
        result_set: SignSet = SignSet()

        for sign in a:
            if sign == "0":
                result_set |= SignSet("0")
            elif sign == "-":
                result_set |= SignSet("+")
            elif sign == "+":
                result_set |= SignSet("-")
            else:
                raise ValueError(f"Invalid sign {sign!r}")

        return result_set

    def _add(self, a: Sign, b: Sign) -> Set[Sign]:    
        if a == "0":
            return { b }
        
        if b == "0":
            return { a }
        
        return {"-", "0", "+"}
        
    def _sub(self, a: Sign, b: Sign) -> Set[Sign]:
        if b == "0":
            return { a }
    
        if b == "-":
            return self._add(a, "+")
        
        if b == "+":
            return self._add(a, "-")
        
        
    def _mul(self, a: Sign, b: Sign) -> Set[Sign]:
        if a == "0" or b == "0":
            return { "0" }
        
        if a == b:
            return { "+" }
        
        return { "-" }
        

    def _div(self, a: Sign, b: Sign) -> Set[Sign]:
        if b == "0":
            raise ZeroDivisionError()
        
        if a == "0":
            return { "0" }
        
        if a == b:
            return { "+" }
        
        return { "-" }

    def _rem(self, a: Sign, b: Sign) -> Set[Sign]:
        if b == "0":
            raise ZeroDivisionError()
        
        return a

    def compare(self, opr: str, a: SignSet, b: SignSet) -> BoolSet:
        combinations = itertools.product(a, b)

        result_set: BoolSet = BoolSet()

        for (a, b) in combinations:
            if opr == "eq":
                result_set |= self._eq(a, b)
            elif opr == "ne":
                result_set |= self._ne(a, b)
            elif opr == "lt":
                result_set |= self._lt(a, b)
            elif opr == "le":
                result_set |= self._le(a, b)
            elif opr == "gt":
                result_set |= self._gt(a, b)
            elif opr == "ge":
                result_set |= self._ge(a, b)
            else:
                raise NotImplementedError(f"can't handle {opr!r}")

        return result_set


    def _le (self, a: Sign, b: Sign) -> BoolSet:
        return self._lt(a, b) | self._eq(a, b)
    
    def _lt (self, a: Sign, b: Sign) -> BoolSet:
        match (a, b):
            case ("+", "+"): return BoolSet( True, False )
            case ("+", _): return BoolSet( False )
            case ("0", "+"): return BoolSet( True )
            case ("0", _): return BoolSet( False )
            case ("-", "-"): return BoolSet( True, False )
            case ("-", _): return BoolSet( True )
    
    def _eq (self, a: Sign, b: Sign) -> BoolSet:
        match (a, b):
            case ("+", "+") | ("-", "-"): return BoolSet( True, False )
            case ("0", "0"): return BoolSet( True )
            case (_, _): return BoolSet( False )
    
    def _ne (self, a: Sign, b: Sign) -> BoolSet:
        match (a, b):
            case ("+", "+") | ("-", "-"): return BoolSet( True, False )
            case ("0", "0"): return BoolSet( False )
            case (_, _): return BoolSet( True )
    
    def _ge (self, a: Sign, b: Sign) -> BoolSet:
        return self._gt(a, b) | self._eq(a, b)
    
    def _gt (self, a: Sign, b: Sign) -> BoolSet:
        match (a, b):
            case ("+", "+"): return BoolSet( True, False )
            case ("+", _): return BoolSet( True )
            case ("0", "+" | "0"): return BoolSet( False )
            case ("0", "-"): return BoolSet( True )
            case ("-", "-"): return BoolSet( True, False )
            case ("-", _): return BoolSet( False )
