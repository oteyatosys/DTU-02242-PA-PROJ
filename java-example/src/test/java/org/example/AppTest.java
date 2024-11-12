package org.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class AppTest {

    @Test
    public void testThruth( ){
        assertTrue( true );
    }

    @Test
    public void testFail( ){
        assertTrue( false );
    }
}
