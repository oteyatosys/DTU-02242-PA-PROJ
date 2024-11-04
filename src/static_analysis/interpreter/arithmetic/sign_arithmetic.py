from dataclasses import dataclass
import itertools
from typing import Set, Tuple
from static_analysis.interpreter.abstractions.bool_set import BoolSet
from static_analysis.interpreter.abstractions.sign_set import SignSet, Sign
from static_analysis.interpreter.arithmetic.arithmetic import Arithmetic

@dataclass
class SignArithmetic(Arithmetic[SignSet]):
    _order: Tuple[Sign] = ("-", "0", "+")

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

            else:
                raise NotImplementedError(f"can't handle {opr!r}")
            
        return SignSet(result_set)

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
        if a != b:
            return BoolSet( self._order.index(a) <= self._order.index(b) )
        
        if a == "0":
            return BoolSet( True )
        
        return BoolSet( True, False )
    
    def _lt (self, a: Sign, b: Sign) -> BoolSet:
        if a != b:
            return BoolSet(self._order.index(a) < self._order.index(b))
        
        if a == "0":
            return BoolSet( False )
        
        return BoolSet( True, False )
    
    def _eq (self, a: Sign, b: Sign) -> BoolSet:
        if a == "0" and b == "0":
            return BoolSet( True )
        
        return BoolSet( True, False )
    
    def _ne (self, a: Sign, b: Sign) -> BoolSet:
        if a == "0" and b == "0":
            return BoolSet( False )
        
        return BoolSet( True, False )
    
    def _ge (self, a: Sign, b: Sign) -> BoolSet:
        if a != b:
            return BoolSet( self._order.index(a) >= self._order.index(b) )
        
        if a == "0":
            return BoolSet( True )
        
        return BoolSet( True, False )
    
    def _gt (self, a: Sign, b: Sign) -> BoolSet:
        if a != b:
            return BoolSet( self._order.index(a) > self._order.index(b) )
        
        if a == "0":
            return BoolSet( False )
        
        return BoolSet( True, False )