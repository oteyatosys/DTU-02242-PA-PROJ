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
    public static void testFactorial() {
        assert App.factorial(0) == 1;
        assert App.factorial(1) == 1;
        assert App.factorial(2) == 2;
        assert App.factorial(3) == 6;
    }
}
