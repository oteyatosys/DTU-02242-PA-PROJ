from typing import Set
from hypothesis import given
from hypothesis.strategies import integers, sets

from static_analysis.interpreter.abstractions.sign_set import SignSet
from static_analysis.interpreter.arithmetic.sign_arithmetic import SignArithmetic

arithmetic = SignArithmetic()

@given(sets(integers()), sets(integers()))
def test_sign_adds(xs, ys):
  assert (
    SignSet.abstract({x + y for x in xs for y in ys}) 
      <= arithmetic.binary("add", SignSet.abstract(xs), SignSet.abstract(ys))
    )

@given(sets(integers()), sets(integers()))
def test_sign_subs(xs, ys):
    assert (
      SignSet.abstract({x - y for x in xs for y in ys}) 
        <= arithmetic.binary("sub", SignSet.abstract(xs), SignSet.abstract(ys))
      )
  
@given(sets(integers()), sets(integers()))
def test_sign_muls(xs, ys):
    assert (
      SignSet.abstract({x * y for x in xs for y in ys}) 
        <= arithmetic.binary("mul", SignSet.abstract(xs), SignSet.abstract(ys))
      )

@given(sets(integers()), sets(integers()))
def test_sign_le(xs, ys):
    assert (
      {x <= y for x in xs for y in ys} 
        <= arithmetic.compare("le", SignSet.abstract(xs), SignSet.abstract(ys))
      )

@given(sets(integers()), sets(integers()))
def test_sign_lt(xs, ys):
    assert (
      {x < y for x in xs for y in ys} 
        <= arithmetic.compare("lt", SignSet.abstract(xs), SignSet.abstract(ys))
      )
    
@given(sets(integers()), sets(integers()))
def test_sign_ge(xs, ys):
    assert (
      {x >= y for x in xs for y in ys} 
        <= arithmetic.compare("ge", SignSet.abstract(xs), SignSet.abstract(ys))
      )

@given(sets(integers()), sets(integers()))
def test_sign_gt(xs, ys):
    assert (
      {x > y for x in xs for y in ys} 
        <= arithmetic.compare("gt", SignSet.abstract(xs), SignSet.abstract(ys))
      )
    
@given(sets(integers()), sets(integers()))
def test_sign_eq(xs, ys):
    assert (
      {x == y for x in xs for y in ys} 
        <= arithmetic.compare("eq", SignSet.abstract(xs), SignSet.abstract(ys))
      )
    
@given(sets(integers()), sets(integers()))
def test_sign_ne(xs, ys):
    assert (
      {x != y for x in xs for y in ys} 
        <= arithmetic.compare("ne", SignSet.abstract(xs), SignSet.abstract(ys))
      )