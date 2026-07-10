package clientapp;

import calcstubs.*;
import calcstubs.Number;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.stub.StreamObserver;

import java.util.*;


public class Client {

    private static String svcIP = "localhost";
    //private static String svcIP = "35.205.202.150";
    private static int svcPort = 8500;
    private static ManagedChannel channel;
    private static CalcServiceGrpc.CalcServiceBlockingStub blockingStub;
    private static CalcServiceGrpc.CalcServiceStub noBlockStub;


    public static void main(String[] args) {
        try {
            if (args.length == 2) {
                svcIP = args[0];
                svcPort = Integer.parseInt(args[1]);
            }
            System.out.println("connect to " + svcIP + ":" + svcPort);
            channel = ManagedChannelBuilder.forAddress(svcIP, svcPort)
                    // Channels are secure by default (via SSL/TLS). For the example we disable TLS to avoid
                    // needing certificates.
                    .usePlaintext()
                    .build();
            blockingStub = CalcServiceGrpc.newBlockingStub(channel);
            noBlockStub = CalcServiceGrpc.newStub(channel);

            while (true) {
                switch (Menu()) {
                    case 1:  // adicionar dois numeros
                        add();
                        break;
                    case 2: // calcular as  potencias de x^y
                        generatePowers();
                        break;
                    case 3: //somar a sequencia dos numeros de x a y
                        addSeqOfNumbers();
                        break;
                    case 4: //sequencia de operacões de soma x + y
                        multipleAdd();
                        break;
                    case 99:
                        System.exit(0);
                    default:
                        break;
                }
            }
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    private static int Menu() {
        int op;
        Scanner scan = new Scanner(System.in);
        do {
            System.out.println();
            System.out.println("    MENU");
            System.out.println(" 1 - Case1 - chamada unária: add two numbers");
            System.out.println(" 2 - Case 2 - chamada com steam de servidor: generate powers");
            System.out.println(" 3 - Case 3 - chamada com stream de cliente: add a sequence of numbers");
            System.out.println(" 4 - stream de cliente e de servidor: Multiple add operations ");
            System.out.println("99 - Exit");
            System.out.println();
            System.out.println("Choose an Option?");
            op = scan.nextInt();
        } while (!((op >= 1 && op <= 4) || op == 99));
        return op;
    }

    static void add() {
        // CHAMADA UNÁRIA
        Result res = blockingStub.add(AddOperands.newBuilder()
                .setId("50+25")
                .setOp1(50)
                .setOp2(25)
                .build());
        System.out.println("add " + res.getId() + "= " + res.getRes());
    }

    static void generatePowers() throws InterruptedException {
        // CHAMADA COM STREAM DO SERVIDOR -
        int base = Integer.parseInt(read("Base: ", new Scanner(System.in)));
        int expoente = Integer.parseInt(read("Expoente: ", new Scanner(System.in)));
        NumberAndMaxExponent numberAndExp = NumberAndMaxExponent
                .newBuilder()
                .setBaseNumber(base)
                .setMaxExponent(expoente)
                .build();

        GeneratePowersStream powersStream = new GeneratePowersStream();
        noBlockStub.generatePowers(numberAndExp, powersStream);
        while(!powersStream.isCompleted()) {
            System.out.println("Continue working...");
            Thread.sleep(1000);
        }
    }

    static void addSeqOfNumbers() {
        // CHAMADA COM STREAM DO CLIENTE
        int N =Integer.parseInt(read("Quantos nº tem a soma?", new Scanner(System.in)));
        // O server é que usa o streamObserver passado como parâmetro para comunicar com o cliente.
        // O Retorno da função é usado pelo cliente para comunicar com o server
        StreamObserver<Number> streamNumbers = noBlockStub.addSeqOfNumbers(new StreamObserver<Result>() {
            @Override
            public void onNext(Result result) {
                System.out.println("Add total: " + result.getRes());
            }

            @Override
            public void onError(Throwable throwable) {
                System.out.println(throwable.getMessage());
            }

            @Override
            public void onCompleted() {
                System.out.println("Add sequence completed");
            }
        });
        for (int i = 1; i <= N; i++) {
            int numero =Integer.parseInt(read("Escreve um número: ", new Scanner(System.in)));
            streamNumbers.onNext(Number.newBuilder().setNum(numero).build());
            System.out.println("Foi enviado o número: " + numero);
        }
        streamNumbers.onCompleted();
    }

    static void multipleAdd() {
        // CHAMA STREAM CLIENETE E STREAM SERVIDOR
        int N = Integer.parseInt(read("Quantas somas quer fazer?", new Scanner(System.in)));
        StreamObserver<AddOperands> streamAddOp = noBlockStub.multipleAdd(new StreamObserver<Result>() {
            @Override
            public void onNext(Result result) {
                System.out.println("Add result of " + result.getId() + " = " + result.getRes());
            }

            @Override
            public void onError(Throwable throwable) {}

            @Override
            public void onCompleted() {
                System.out.println("Multiple Add completed.");
            }
        });

        for(int i = 1; i <= N; i++) {
            int op1 = Integer.parseInt(read("Operando1:", new Scanner(System.in)));
            int op2 = Integer.parseInt(read("Operando2:", new Scanner(System.in)));
            AddOperands addOperands = AddOperands.newBuilder()
                    .setId(op1 + "+" + op2)
                    .setOp1(op1)
                    .setOp2(op2)
                    .build();
            streamAddOp.onNext(addOperands);
        }
        streamAddOp.onCompleted();
    }

    private static String read(String msg, Scanner input) {
        System.out.println(msg);
        return input.nextLine();
    }
}
