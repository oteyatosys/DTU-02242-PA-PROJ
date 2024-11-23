from dataclasses import dataclass
from typing import TypeAlias

from static_analysis.interpreter.abstractions.bool_set import BoolSet


Boundary : TypeAlias = float | int
@dataclass
class Interval():
    lb : Boundary
    ub : Boundary

    def __le__(self, other: 'Interval') -> bool:
        return (self.lb >= other.lb and self.ub <= other.ub)
    
    def __and__(self, other: 'Interval') -> 'Interval':
        lower_bounds = max(self.lb,other.lb)
        upper_bounds = min(self.ub,other.ub)
        if lower_bounds > upper_bounds :
            return Interval.bot()
        return Interval(lower_bounds,upper_bounds)
    
    def __or__(self, other: 'Interval') -> 'Interval':
        if isinstance(other, set):
            return self
        return Interval(min(self.lb,other.lb),max(self.ub,other.ub))
    
    def __contains__(self, member: int):
        return (self.lb <= member and member <= self.ub)
    
    def __str__(self):
        return f"[{self.lb}, {self.ub}]"
    
    def widening(self, K : set[int], other: 'Interval'):
        if isinstance(other, set):
            other = Interval.bot()
        lower_bounds = max((k for k in K if k <= min(self.lb,other.lb)), default=float("-inf"))
        upper_bounds = min((k for k in K if k >= max(self.ub,other.ub)), default=float("inf"))
        return Interval(lower_bounds,upper_bounds)
        
    def __eq__(self, value):
        if not(isinstance(value,Interval)):
            return False
        return self.lb == value.lb and self.ub == value.ub
    
    def __repr__(self):
        return f"[{self.lb}, {self.ub}]"
    
    def __hash__(self):
        return hash((self.lb, self.ub))
    
    @staticmethod
    def abstract(items: set[int]):
        if len(items) == 0 :
            return Interval(float("inf"),float("-inf"))
        return Interval(min(items),max(items))
    @staticmethod
    def bot() -> 'Interval':
        return Interval(float("inf"),float("-inf"))
    
    @staticmethod
    def top() -> 'Interval':
        return Interval(float("-inf"),float("inf"))
    
    @staticmethod
    def from_boolset(boolset: BoolSet) -> 'Interval':
        lb: Boundary = float("inf")
        ub: Boundary = float("-inf")
        for value in boolset:
            if value:
                lb = min(lb, 1)
                ub = max(ub, 1)
            else:
                lb = min(lb, 0)
                ub = max(ub, 0)
        return Interval(lb, ub)