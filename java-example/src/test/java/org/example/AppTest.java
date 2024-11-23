package org.example;

import org.junit.jupiter.api.Test;

public class AppTest {

    @Test
    public void testThruth( ){
        assert true;
    }

    @Test
    public void testFactorial() {
        assert App.factorial(0) == 1;
        assert App.factorial(1) == 1;
        assert App.factorial(2) == 2;
        assert App.factorial(3) == 6;
    }

    @Test
    public void testReturn( ){
        assert true;
    }

    @Test
    public void testGetInt( ){
        assert 42 == App.getNum();
    }

    public static int testReturn2( ){
        boolean b = true;

        if (b) {
            return 42;
        } else {
            return -1;
        }
    }

    @Test
    public void testReturn3( ){
        assert AppTest.testReturn2() > 0;
    }
}
