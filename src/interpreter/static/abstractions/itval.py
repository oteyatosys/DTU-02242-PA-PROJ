from dataclasses import dataclass
from typing import List, Set, Tuple, TypeAlias, Literal



Boundary : TypeAlias = float | int
@dataclass
class Interval():
    lb : Boundary
    ub : Boundary

    def __le__(self, other: 'Interval') -> bool:
        return (self.lb >= other.lb and self.ub <= other.ub)
    
    def __and__(self, other: 'Interval') -> 'Interval':
        return Interval(max(self.lb,other.lb),min(self.ub,other.ub))
    
    def __or__(self, other: 'Interval') -> 'Interval':
        if isinstance(other, set):
            return self
        return Interval(min(self.lb,other.lb),max(self.ub,other.ub))
    
    def __contains__(self, member: int):
        return (self.lb <= member and member <= self.ub)
    
    def widening(self, K : set[int], other: 'Interval'):
        lower_bounds = max((k for k in K if k <= min(self.lb,other.lb)), default=float("-inf"))
        upper_bounds = min((k for k in K if k >= max(self.ub,other.ub)), default=float("inf"))
        return Interval(lower_bounds,upper_bounds)
        
    def __eq__(self, other):
        return (self.lb == other.lb and self.ub == other.ub)
    
    def __repr__(self):
        return super().__repr__()
    
    def __hash__(self):
        return super().__hash__()
    
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


    
