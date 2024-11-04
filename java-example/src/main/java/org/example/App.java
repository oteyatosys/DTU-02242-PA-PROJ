package org.example;

public class App {

    public static final int VERSION = 666;

    public static int add5(int a){
        return a + 5;
    }

    public static int convertBytesToBits(int a){
        return a * 8;
    }

    public static String getGreeting(String greeting, String name){
        return greeting + ", " + name + "!";
    }

    public static String getGreeting(String name){
        return getGreeting("Hello", name);
    }

    // We make a test method that also utilizes geneics
    public static <T> String getGreeting(String greeting, T name){
        return greeting + ", " + name + "!";
    }

    public static void main( String[] args ){
        System.out.println( getGreeting("Yo", "World") );
    }
}
