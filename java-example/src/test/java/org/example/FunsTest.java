package org.example;

import org.junit.jupiter.api.Test;

public class FunsTest {

    @Test
    public static void testRun1() {
        assert Funs.run(1) == 0;
    }

    @Test
    public static void testRun2() {
        assert Funs.run(2) == 0;
    }

    @Test
    public static void testRun3() {
        assert Funs.run(3) == 0;
    }
}
