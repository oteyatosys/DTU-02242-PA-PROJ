package org.example;

import org.junit.jupiter.api.Test;

public class MathTest {

    @Test
    public void testNegate() {
        assert Math.negate(5) == -5;
    }

    @Test
    public void testNegateNegative() {
        assert Math.negate(-5) == 5;
    }

    @Test
    public void testNegateZero() {
        assert Math.negate(0) == 0;
    }

    @Test
    public void testAbsPositive() {
        assert Math.abs(5) == 5;
    }

    @Test
    public void testAbsNegative() {
        assert Math.abs(-5) == 5;
    }

    @Test
    public void testAbsZero() {
        assert Math.abs(0) == 0;
    }

    @Test
    public void testGcd() {
        assert Math.gcd(48, 18) == 6;
    }

    @Test
    public void testGcdCoprime() {
        assert Math.gcd(101, 103) == 1;
    }

    @Test
    public void testGcdWithZero() {
        assert Math.gcd(0, 5) == 5;
    }

    @Test
    public void testLcm() {
        assert Math.lcm(4, 6) == 12;
    }

    @Test
    public void testLcmWithZero() {
        assert Math.lcm(0, 5) == 0;
    }

    @Test
    public void testFactorialZero() {
        assert Math.factorial(0) == 1;
    }

    @Test
    public void testFactorialOne() {
        assert Math.factorial(1) == 1;
    }

    @Test
    public void testFactorialFour() {
        assert Math.factorial(4) == 24;
    }

    @Test
    public void testFibonacciZero() {
        assert Math.fibonacci(0) == 0;
    }

    @Test
    public void testFibonacciOne() {
        assert Math.fibonacci(1) == 1;
    }

    @Test
    public void testFibonacciFive() {
        assert Math.fibonacci(5) == 5;
    }

    @Test
    public void testDividesByTrue() {
        assert Math.dividesBy(10, 2);
    }

    @Test
    public void testDividesByFalse() {
        assert !Math.dividesBy(10, 3);
    }

    @Test
    public void testIsPrimeTrue() {
        assert Math.isPrime(17);
    }

    @Test
    public void testIsPrimeFalse() {
        assert !Math.isPrime(18);
    }

    @Test
    public void testIsPrimeEdgeCase() {
        assert !Math.isPrime(1);
    }

    @Test
    public void testDivide2() {
        assert Math.divide2(10, 2) == 3;
    }
}
