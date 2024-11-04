from typing import Set
from hypothesis import given
from hypothesis.strategies import sets, integers

from static_analysis.interpreter.abstractions.sign_set import SignSet

@given(sets(integers()))
def test_valid_abstraction(xs: Set[int]):
    s = SignSet.abstract(xs)
    assert all(x in s for x in xs)