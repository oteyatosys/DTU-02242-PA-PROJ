package org.example;

import org.junit.jupiter.api.Test;

public class AppTest {

    @Test
    public void testThruth( ){
        assert true;
    }

    @Test
    public void testGetNum() {
        assert App.getNum() == 42;
    }

    @Test
    public void testAdd5() {
        assert App.add5(0) == 5;
        assert App.add5(1) == 6;
        assert App.add5(2) == 7;
        assert App.add5(3) == 8;
    }

    @Test
    public void testConvertBytesToBits() {
        assert App.convertBytesToBits(0) == 0;
        assert App.convertBytesToBits(1) == 8;
        assert App.convertBytesToBits(2) == 16;
        assert App.convertBytesToBits(3) == 24;
    }

    @Test
    public void testFactorial() {
        assert App.factorial(0) == 1;
        assert App.factorial(1) == 1;
        assert App.factorial(2) == 2;
        assert App.factorial(3) == 6;
    }

    @Test
    public void testSomeLoops() {
        assert App.someLoops() == 1000000;
    }

    @Test
    public void testComplexFunction() {
        assert App.complexFunction(0) == 5;
        assert App.complexFunction(1) == 47;
        assert App.complexFunction(2) == 89;
        assert App.complexFunction(3) == 131;
    }

    @Test
    public void testInefficientFunction() {
        assert App.inefficientFunction(0) == 0;
        assert App.inefficientFunction(-10) == 0;
        assert App.inefficientFunction(1) == 1;
        assert App.inefficientFunction(2) == 1;
        assert App.inefficientFunction(3) == 2;
        assert App.inefficientFunction(4) == 3;
        assert App.inefficientFunction(10) == 55;      
    }

    @Test
    public void testCallingInefficientFunction() {
        assert App.callingInefficientFunction() == 102334155;
    }

    @Test
    public void testIsN238() {
        assert App.isN238(0) == 0;
        assert App.isN238(238) == 100;
        assert App.isN238(10) == 0;
        assert App.isN238(-18280) == 0;
    }
    
}
