package org.example;

import org.junit.jupiter.api.Test;

public class FunsTest {

    @Test
    public void testZero() {
        assert Funs.run(0) == 0;
    }

    @Test
    public void testOne() {
        assert Funs.run(1) == 0;
    }

    @Test
    public void testTwo() {
        assert Funs.run(2) == 0;
    }
}
