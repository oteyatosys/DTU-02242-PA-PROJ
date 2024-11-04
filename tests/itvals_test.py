from hypothesis import given
from hypothesis.strategies import integers, sets
from interpreter.static.abstractions.itval import Interval

@given(sets(integers()))
def test_interval_abstraction_valid(xs):
  r = Interval.abstract(xs) 
  assert all(x in r for x in xs)

@given(sets(integers()), sets(integers()))
def test_interval_abstraction_distributes(xs, ys):
  assert (Interval.abstract(xs) | Interval.abstract(ys)) == Interval.abstract(xs | ys)

if __name__ == "__main__":
    test_interval_abstraction_valid()
    test_interval_abstraction_distributes()