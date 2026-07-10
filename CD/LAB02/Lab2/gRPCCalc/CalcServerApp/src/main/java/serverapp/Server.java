package serverapp;

import calcstubs.*;
import calcstubs.Number;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;

import java.util.Random;


public class Server extends CalcServiceGrpc.CalcServiceImplBase {

    private static int svcPort = 8500;

    public static void main(String[] args) {
        try {
            if (args.length > 0) svcPort = Integer.parseInt(args[0]);
            io.grpc.Server svc = ServerBuilder
                .forPort(svcPort)
                .addService(new Server())
                .build();
            svc.start();
            System.out.println("Server started, listening on " + svcPort);
            
            svc.awaitTermination();
            svc.shutdown();

        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    @Override
    public void add(AddOperands request, StreamObserver<Result> responseObserver) {
        /**
         * CHAMADA UNÁRIA
         */
        Result result = Result.newBuilder()
                .setId(request.getId())
                .setRes(request.getOp1() + request.getOp2())
                .build();
        responseObserver.onNext(result);

        responseObserver.onCompleted();
    }

    @Override
    public void generatePowers(NumberAndMaxExponent request, StreamObserver<Result> responseObserver) {
        /**
         * STREAMING SERVIDOR
         */
        for (int i = 1; i <= request.getMaxExponent(); i++) {
            int res = (int)Math.pow(request.getBaseNumber(), i);
            Result result = Result.newBuilder()
                    .setId(request.getId())
                    .setRes(res)
                    .build();
            responseObserver.onNext(result);
            simulateExecutionTime();
        }
        responseObserver.onCompleted();
    }

    @Override
    public StreamObserver<Number> addSeqOfNumbers(StreamObserver<Result> responseObserver) {
        /**
         * STREAMING CLIENTE
         *  - Neste caso só o cliente é que envia por por stream, por isso o server retorna com StreamObserver
         *  - Contudo, o server, que neste caso envia apenas a resposta final, também usa como argumento
         *    o StreamObvserver para enviar a única resposta ao cliente
         */
        System.out.println("AddSeqOfNumbers called.");
        return new StreamObserver<Number>() {
            int soma = 0;
            @Override
            public void onNext(Number number) {
                System.out.println("Vai somar "+ number.getNum());
                soma += number.getNum();
            }

            @Override
            public void onError(Throwable throwable) {}

            @Override
            public void onCompleted() {
                System.out.println("Cliente finalizou requests -> COMPLETED");
                responseObserver.onNext(Result.newBuilder().setRes(soma).build());
                responseObserver.onCompleted();
            }
        };
    }

    @Override
    public StreamObserver<AddOperands> multipleAdd(StreamObserver<Result> responseObserver) {
        //STREAMING CLIENTE E SERVIDOR
        System.out.println("MultipleAdd called.");
        return new StreamObserver<AddOperands>() {
            @Override
            public void onNext(AddOperands addOperands) {
                System.out.println("Vai somar: "+ addOperands.getId());
                simulateExecutionTime();
                Result result = Result.newBuilder()
                        .setId(addOperands.getId())
                        .setRes(addOperands.getOp1() + addOperands.getOp2())
                        .build();
                responseObserver.onNext(result);
                System.out.println("  Result of ID=" + addOperands.getId() + "=" + result.getRes());
            }

            @Override
            public void onError(Throwable throwable) {}

            @Override
            public void onCompleted() {
                System.out.println("Cliente terminou requests -> Completed");
                responseObserver.onCompleted();
            }
        };
    }

    private void simulateExecutionTime() {
        try {
            // simulate processing time between 200ms and 3s
            Thread.sleep(new Random().nextInt(2800) + 200);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
