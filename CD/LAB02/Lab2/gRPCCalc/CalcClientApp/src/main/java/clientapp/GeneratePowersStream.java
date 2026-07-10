package clientapp;

import calcstubs.Number;
import calcstubs.Result;
import io.grpc.stub.StreamObserver;

public class GeneratePowersStream implements StreamObserver<Result> {
    boolean completed=false;

    @Override
    public void onNext(Result result) {
        System.out.println("Uma potência:" + result.getRes());
    }

    @Override
    public void onError(Throwable throwable) {
        System.out.println("Completed with error:"+throwable.getMessage());
        completed=true;
    }

    @Override
    public void onCompleted() {
        System.out.println("Generate Powers completed");
        completed=true;
    }

    public boolean isCompleted() {
        return completed;
    }
}
