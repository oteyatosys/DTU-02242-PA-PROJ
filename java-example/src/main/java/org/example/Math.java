package org.example;

public class Math {

    // Negate a number (e.g., 5 -> -5, -5 -> 5)
    public static int negate(int n) {
        return -n;
    }

    // Absolute value of a number using negate
    public static int abs(int n) {
        return (n < 0) ? negate(n) : n;
    }

    // Calculate the greatest common divisor (GCD) of two integers
    public static int gcd(int a, int b) {
        a = abs(a);
        b = abs(b);
        while (b != 0) {
            int temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    // Calculate the least common multiple (LCM) using GCD
    public static int lcm(int a, int b) {
        // LCM formula: |a * b| / GCD(a, b)
        return abs(a * b) / gcd(a, b);
    }

    // Calculate the factorial of a non-negative integer
    public static int factorial(int n){
        return n == 0 ? 1 : n * factorial(n - 1);
    }

    // Calculate the nth Fibonacci number using recursion
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }

    public static boolean dividesBy(int a, int b) {
        return a % b == 0;
    }

    public static boolean isPrime(int n) {
        if (n <= 1) return false;
        for (int i = 2; i <= n / 2; i++) {
            if (dividesBy(n, i)) return false;
        }
        return true;
    }
}
