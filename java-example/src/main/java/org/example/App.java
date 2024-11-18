package org.example;

public class App {

    public static final int VERSION = 666;

    public static int getNum(){
        return 42;
    }

    public static int add5(int a){
        return a + 5;
    }

    public static String repeat(String s, int n){
        return s.repeat(n);
    }

    public static int convertBytesToBits(int a){
        return a * 8;
    }

    public static int factorial(int n){
        return n == 0 ? 1 : n * factorial(n - 1);
    }

    public static String getGreeting(String greeting, String name){
        return greeting + ", " + name + "!";
    }

    public static String getGreeting(String name){
        return getGreeting("Hello", name);
    }

    public static void main( String[] args ){
        System.out.println( getGreeting("Yo", "World") );
    }
}
