from hypothesis import given
from hypothesis.strategies import integers, sets
from static_analysis.interpreter.abstractions.interval import Interval
from static_analysis.interpreter.arithmetic.interval_arithmetic import IntervalArithmetic

@given(sets(integers()), sets(integers()))
def test_interval_abstraction_add(xs,ys):
  r = IntervalArithmetic.binary('add',Interval.abstract(xs), Interval.abstract(ys))
  assert all(x + y in r for x in xs for y in ys)   
