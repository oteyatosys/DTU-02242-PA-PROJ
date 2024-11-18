package org.example;

import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

public class AppTest {

    @Test
    public static void testThruth( ){
        assert true;
    }

    @Test
    public static void testFail( ){
        assert false;
    }

    @Test
    public static void testFactorial() {
        assert App.factorial(0) == 1;
        assert App.factorial(1) == 1;
        assert App.factorial(2) == 2;
        assert App.factorial(3) == 6;
    }

    @Test
    public int testReturn( ){
        assertTrue( true );
        return 42;
    }

    @Test
    public void testGetInt( ){
        assert 42 == App.getNum();
    }

    @Test
    public void testRepeat( ){
        assert "HelloHelloHello".equals(App.repeat("Hello", 3));
    }

    @Test
    public void testStringEquality( ){
        assert "hejsa".equals("hallo");
    }
}
