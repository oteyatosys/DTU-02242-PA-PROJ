package org.example;

import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

public class AppTest {

    @Test
    public static void testThruth( ){
        assertTrue( true );
    }

    @Test
    public static void testFail( ){
        assertTrue( false );
    }

    @Test
    public static void testGetNum() {
        assert App.getNum() == 42;
    }

    @Test
    public static void testAdd5() {
        assert App.add5(0) == 5;
        assert App.add5(1) == 6;
        assert App.add5(2) == 7;
        assert App.add5(3) == 8;
    }

    @Test
    public static void testConvertBytesToBits() {
        assert App.convertBytesToBits(0) == 0;
        assert App.convertBytesToBits(1) == 8;
        assert App.convertBytesToBits(2) == 16;
        assert App.convertBytesToBits(3) == 24;
    }

    @Test
    public static void testFactorial() {
        assert App.factorial(0) == 1;
        assert App.factorial(1) == 1;
        assert App.factorial(2) == 2;
        assert App.factorial(3) == 6;
    }

    @Test
    public static void testGetgreetings1() {
        assert App.getGreeting("","") == ", !";
        assert App.getGreeting("Hello","zyedeshi") == "Hello, zyedeshi!";
    }

    @Test
    public static void testGetgreetings2() {
        assert App.getGreeting("") == "Hello, !";
        assert App.getGreeting("yfdqzqd124") == "Hello, yfdqzqd124!";
    }

    @Test
    public static void testSomeLoops() {
        assert App.someLoops() == 1000000;
    }

    @Test
    public static void testComplexFunction() {
        assert App.complexFunction(0) == 5;
        assert App.complexFunction(1) == 47;
        assert App.complexFunction(2) == 89;
        assert App.complexFunction(3) == 131;
    }

    @Test
    public static void testInefficientFunction() {
        assert App.inefficientFunction(0) == 0;
        assert App.inefficientFunction(-10) == 0;
        assert App.inefficientFunction(1) == 1;
        assert App.inefficientFunction(2) == 1;
        assert App.inefficientFunction(3) == 2;
        assert App.inefficientFunction(4) == 3;
        assert App.inefficientFunction(10) == 55;      
    }

    @Test
    public static void testCallingInefficientFunction() {
        assert App.callingInefficientFunction() == 102334155;
    }

    @Test
    public static void testIsN238() {
        assert App.isN238(0) == 0;
        assert App.isN238(238) == 100;
        assert App.isN238(10) == 0;
        assert App.isN238(-18280) == 0;
    }
    
    
    

    
}
