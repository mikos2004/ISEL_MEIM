# Lab 2

## Relação entre ficheiro proto e a class que Server extende
O ficheiro proto têm o `service CalcService`. Daí vem o nome de `CalcServiceGrpc.CalcServiceImplBase`.

Dentro do proto tem:
```protobuf
service CalcService {
     rpc add(AddOperands) returns (Result);
     rpc generatePowers (NumberAndMaxExponent) returns (stream Result);
     rpc addSeqOfNumbers (stream Number) returns (Result);
     rpc multipleAdd(stream AddOperands) returns (stream Result);
}
```

Por isso, o Server.java extende de CalcServiceGrpc.CalcServiceImplBase e faz override das funções acima descritas, onde os streams são StreamObserver.

---

## Lado do Server


_Chamada Unária_(1) e _Streaming do Servidor_(2) são feitos da seguinte forma, mesmo que no primeiro caso o server só envie uma reposta.

``` java
public void oper(RequestType request, StreamObserver<ReplyType> responseObserver)
```

Nos casos de _Streming do Cliente_(3) e _Streaming de cliente & servidor_(4) (ou seja, basta o cliente ser streaming) é:
(Stream dos dois lados):
``` java
public StreamObserver<RequestType> oper(StreamObserver<ReplyType> responseObserver)
```
```
NOTA: responseObserver é o canal que o server usa para enviar mensagens ao cliente, usando o onNext() e onComplete().

NOTA: O retorno dos casos (3) e (4) é o canal que o cliente vai usar para enviar mensagens ao server.
```
---

# Casos do Lab2

## Análise das assinaturas das funções do server

Chamada unária e Streaming de Servidor:
``` java
// Chamada unária
public void add(AddOperands request, StreamObserver<Result> responseObserver)

// Chamada Streaming do Servidor
public void generatePowers(NumberAndMaxExponent request, StreamObserver<Result> responseObserver)
```

Como o cliente só vai enviar uma mensagem, envia o request pelo parâmetro.
Ambas as funções retornam void, porque o server não retorna pela função, mas retorna a resposta pelo StreamObserver.

---
Chamada Streaming Cliente, e Streaming de Cliente & Servidor:
```java
// Streaming Cliente
public StreamObserver<Number> addSeqOfNumbers(StreamObserver<Result> responseObserver)

// Streaming Cliente e Servidor
public StreamObserver<AddOperands> multipleAdd(StreamObserver<Result> responseObserver)
```

Em ambos os casos `responseObserver` serve para mensagens ao cliente (no cenário Streaming Cliente, o server só envia uma resposta).

O returnos é o canal que que o cliente usará para enviar os seus dados em stream.

---

## Análise caso chamada unária (1)
```java
@Override
public void add(AddOperands request, StreamObserver<Result> responseObserver) {
    Result result = Result.newBuilder()
            .setId(request.getId())
            .setRes(request.getOp1() + request.getOp2())
            .build();
    responseObserver.onNext(result);
    responseObserver.onCompleted();
}
```

1) Server constrói instância do tipo de StreamObserver do responseObserver;
2) Usa _responseObserver.onNext()_ para enviar resposta;
3) Usa _responseObserver.onComplete()_ indicar conclusão.

---

## Análise caso Streaming servidor (2)
``` java
@Override
public void generatePowers(NumberAndMaxExponent request, StreamObserver<Result> responseObserver) {
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
```

1) A cada iteração do ciclo for, o server constrói um _Result_ e envia ao cliente com _responseObserver.onNext()_
2) No final usa _responseObserver.onComplete()_.

---

## Análise Streaming Cliente (3)
```java
@Override
public StreamObserver<Number> addSeqOfNumbers(StreamObserver<Result> responseObserver) {
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
```

1) O servidor criar um StreamObserver para o Cliente poder enviar os seus dados para o servidor.
2) _onNext()_ representa o que o servidor vai fazer quando receber um número.
3) _onComplete()_ representa o que o servidor faz quando o cliente indica que terminou de enviar dados.

Estes _onNext()_ e _onComplete()_ são chamados pelo cliente e descrevem o que o servidor fará.
Neste caso o servidor só enviar para o cliente (só usa responseObserver) no _onComplete()_ porque só envia uma resposta.

---

## Análise Streaming Cliente e Servidor
```java
@Override
public StreamObserver<AddOperands> multipleAdd(StreamObserver<Result> responseObserver) {
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
```

1) O servidor criar um StreamObserver para o Cliente poder enviar os seus dados para o servidor.
2) _onNext()_ representa o que o servidor vai fazer quando receber um número.
3) _onComplete()_ representa o que o servidor faz quando o cliente indica que terminou de enviar dados.

Neste caso, como o servidor também está em streaming, a cada _onNext()_ envia o resultado da soma pelo _responseObserver_. No _onComplete()_ indica apenas ao cliente que também termina.

---
---
---
---
---

# Lado do cliente

```
Nota: As operações do lado do cliente podem ser bloqueantes(blockingStub) ou não bloqueantes(noBlockStub).
- blockingStub.oper(_request_)
- noBlockStub.oper(_request_, _StreamingObserver_) - por onde o servidor envia as respostas

Nota: Todas as funções do lado do cliente são sem parâmetros e sem retornos.
```

## Análise caso chamada unária (1) - Caso bloqueante
```java
static void add() {
    Result res = blockingStub.add(AddOperands.newBuilder()
        .setId("50+25")
        .setOp1(50)
        .setOp2(25)
        .build());
    System.out.println("add " + res.getId() + "= " + res.getRes());
}
```

1) Cliente usa _blockingStub.oper()_, passando como parâmetro o request.
2) Usa do _Result_ para dar print do resultado.

Nota: Ou seja, `rpc add(AddOperands) returns (Result);`

---

## Análise caso Streaming servidor (2) - cao não bloquante
```java
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
```

