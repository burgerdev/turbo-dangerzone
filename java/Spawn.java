


class MyT extends Thread {
    private static final int SLEEP_S = 5;
    @Override
    public void run() {
        try {
        Thread.sleep(SLEEP_S*1000);
        }
        catch(InterruptedException ex) {
        }

    }
}

public class Spawn {
    private static final int NUM_THREADS = 1000000;

public static void main(String[] args) throws Exception {
    int n = NUM_THREADS;
    if (args.length > 0) {
        n = Integer.parseInt(args[0]);
    }
    System.out.printf("Creating %d threads...\n", n);

    MyT[] arr = new MyT[n];
    for (int i=0; i<arr.length; i++) {
        MyT t = new MyT();
        //System.out.println(i);
        try {
        t.start();
        } catch(OutOfMemoryError err) {
            System.out.printf("Got to thread %d\n", i);
            throw err;
        }
        arr[i] = t;
    }

    for (int i=0; i<arr.length; i++) {
        arr[i].join();
    }

}
}
