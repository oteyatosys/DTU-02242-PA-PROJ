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

    public static int someLoops(){
        int i = 0;
        while (i < 1000000) i++;
        return i;
    }

    public static int complexFunction(int i){
        return add5(getNum()*i);
    }

    public static int inefficientFunction(int i){
        if (i < 1) return 0;
        else if (i == 1) return 1;
        else return inefficientFunction(i-1) + inefficientFunction(i-2);
    }

    public static int callingInefficientFunction(){
        return inefficientFunction(40);
    }
    
    public static int isN238(int n){
        if (n == 238) return 100;
        else return 0;
    }
}
