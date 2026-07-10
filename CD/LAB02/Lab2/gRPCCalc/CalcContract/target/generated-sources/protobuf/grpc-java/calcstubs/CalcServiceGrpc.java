package calcstubs;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 * <pre>
 * serviço com operações sobre números
 * </pre>
 */
@io.grpc.stub.annotations.GrpcGenerated
public final class CalcServiceGrpc {

  private CalcServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "calcservice.CalcService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<calcstubs.AddOperands,
      calcstubs.Result> getAddMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "add",
      requestType = calcstubs.AddOperands.class,
      responseType = calcstubs.Result.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<calcstubs.AddOperands,
      calcstubs.Result> getAddMethod() {
    io.grpc.MethodDescriptor<calcstubs.AddOperands, calcstubs.Result> getAddMethod;
    if ((getAddMethod = CalcServiceGrpc.getAddMethod) == null) {
      synchronized (CalcServiceGrpc.class) {
        if ((getAddMethod = CalcServiceGrpc.getAddMethod) == null) {
          CalcServiceGrpc.getAddMethod = getAddMethod =
              io.grpc.MethodDescriptor.<calcstubs.AddOperands, calcstubs.Result>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "add"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  calcstubs.AddOperands.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  calcstubs.Result.getDefaultInstance()))
              .setSchemaDescriptor(new CalcServiceMethodDescriptorSupplier("add"))
              .build();
        }
      }
    }
    return getAddMethod;
  }

  private static volatile io.grpc.MethodDescriptor<calcstubs.NumberAndMaxExponent,
      calcstubs.Result> getGeneratePowersMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "generatePowers",
      requestType = calcstubs.NumberAndMaxExponent.class,
      responseType = calcstubs.Result.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<calcstubs.NumberAndMaxExponent,
      calcstubs.Result> getGeneratePowersMethod() {
    io.grpc.MethodDescriptor<calcstubs.NumberAndMaxExponent, calcstubs.Result> getGeneratePowersMethod;
    if ((getGeneratePowersMethod = CalcServiceGrpc.getGeneratePowersMethod) == null) {
      synchronized (CalcServiceGrpc.class) {
        if ((getGeneratePowersMethod = CalcServiceGrpc.getGeneratePowersMethod) == null) {
          CalcServiceGrpc.getGeneratePowersMethod = getGeneratePowersMethod =
              io.grpc.MethodDescriptor.<calcstubs.NumberAndMaxExponent, calcstubs.Result>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "generatePowers"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  calcstubs.NumberAndMaxExponent.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  calcstubs.Result.getDefaultInstance()))
              .setSchemaDescriptor(new CalcServiceMethodDescriptorSupplier("generatePowers"))
              .build();
        }
      }
    }
    return getGeneratePowersMethod;
  }

  private static volatile io.grpc.MethodDescriptor<calcstubs.Number,
      calcstubs.Result> getAddSeqOfNumbersMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "addSeqOfNumbers",
      requestType = calcstubs.Number.class,
      responseType = calcstubs.Result.class,
      methodType = io.grpc.MethodDescriptor.MethodType.CLIENT_STREAMING)
  public static io.grpc.MethodDescriptor<calcstubs.Number,
      calcstubs.Result> getAddSeqOfNumbersMethod() {
    io.grpc.MethodDescriptor<calcstubs.Number, calcstubs.Result> getAddSeqOfNumbersMethod;
    if ((getAddSeqOfNumbersMethod = CalcServiceGrpc.getAddSeqOfNumbersMethod) == null) {
      synchronized (CalcServiceGrpc.class) {
        if ((getAddSeqOfNumbersMethod = CalcServiceGrpc.getAddSeqOfNumbersMethod) == null) {
          CalcServiceGrpc.getAddSeqOfNumbersMethod = getAddSeqOfNumbersMethod =
              io.grpc.MethodDescriptor.<calcstubs.Number, calcstubs.Result>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.CLIENT_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "addSeqOfNumbers"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  calcstubs.Number.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  calcstubs.Result.getDefaultInstance()))
              .setSchemaDescriptor(new CalcServiceMethodDescriptorSupplier("addSeqOfNumbers"))
              .build();
        }
      }
    }
    return getAddSeqOfNumbersMethod;
  }

  private static volatile io.grpc.MethodDescriptor<calcstubs.AddOperands,
      calcstubs.Result> getMultipleAddMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "multipleAdd",
      requestType = calcstubs.AddOperands.class,
      responseType = calcstubs.Result.class,
      methodType = io.grpc.MethodDescriptor.MethodType.BIDI_STREAMING)
  public static io.grpc.MethodDescriptor<calcstubs.AddOperands,
      calcstubs.Result> getMultipleAddMethod() {
    io.grpc.MethodDescriptor<calcstubs.AddOperands, calcstubs.Result> getMultipleAddMethod;
    if ((getMultipleAddMethod = CalcServiceGrpc.getMultipleAddMethod) == null) {
      synchronized (CalcServiceGrpc.class) {
        if ((getMultipleAddMethod = CalcServiceGrpc.getMultipleAddMethod) == null) {
          CalcServiceGrpc.getMultipleAddMethod = getMultipleAddMethod =
              io.grpc.MethodDescriptor.<calcstubs.AddOperands, calcstubs.Result>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.BIDI_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "multipleAdd"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  calcstubs.AddOperands.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  calcstubs.Result.getDefaultInstance()))
              .setSchemaDescriptor(new CalcServiceMethodDescriptorSupplier("multipleAdd"))
              .build();
        }
      }
    }
    return getMultipleAddMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static CalcServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CalcServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CalcServiceStub>() {
        @java.lang.Override
        public CalcServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CalcServiceStub(channel, callOptions);
        }
      };
    return CalcServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports all types of calls on the service
   */
  public static CalcServiceBlockingV2Stub newBlockingV2Stub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CalcServiceBlockingV2Stub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CalcServiceBlockingV2Stub>() {
        @java.lang.Override
        public CalcServiceBlockingV2Stub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CalcServiceBlockingV2Stub(channel, callOptions);
        }
      };
    return CalcServiceBlockingV2Stub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static CalcServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CalcServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CalcServiceBlockingStub>() {
        @java.lang.Override
        public CalcServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CalcServiceBlockingStub(channel, callOptions);
        }
      };
    return CalcServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static CalcServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<CalcServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<CalcServiceFutureStub>() {
        @java.lang.Override
        public CalcServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new CalcServiceFutureStub(channel, callOptions);
        }
      };
    return CalcServiceFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   * serviço com operações sobre números
   * </pre>
   */
  public interface AsyncService {

    /**
     * <pre>
     * add two numbers
     * </pre>
     */
    default void add(calcstubs.AddOperands request,
        io.grpc.stub.StreamObserver<calcstubs.Result> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getAddMethod(), responseObserver);
    }

    /**
     * <pre>
     * generate the number powers with exponents betwwen 1 and maximum 
     * </pre>
     */
    default void generatePowers(calcstubs.NumberAndMaxExponent request,
        io.grpc.stub.StreamObserver<calcstubs.Result> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGeneratePowersMethod(), responseObserver);
    }

    /**
     * <pre>
     * add a sequence of numbers, ex: 1,2, 10, 5 = 18
     * </pre>
     */
    default io.grpc.stub.StreamObserver<calcstubs.Number> addSeqOfNumbers(
        io.grpc.stub.StreamObserver<calcstubs.Result> responseObserver) {
      return io.grpc.stub.ServerCalls.asyncUnimplementedStreamingCall(getAddSeqOfNumbersMethod(), responseObserver);
    }

    /**
     * <pre>
     * Multiple add operations using a bidirecional stream
     * </pre>
     */
    default io.grpc.stub.StreamObserver<calcstubs.AddOperands> multipleAdd(
        io.grpc.stub.StreamObserver<calcstubs.Result> responseObserver) {
      return io.grpc.stub.ServerCalls.asyncUnimplementedStreamingCall(getMultipleAddMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service CalcService.
   * <pre>
   * serviço com operações sobre números
   * </pre>
   */
  public static abstract class CalcServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return CalcServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service CalcService.
   * <pre>
   * serviço com operações sobre números
   * </pre>
   */
  public static final class CalcServiceStub
      extends io.grpc.stub.AbstractAsyncStub<CalcServiceStub> {
    private CalcServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CalcServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CalcServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * add two numbers
     * </pre>
     */
    public void add(calcstubs.AddOperands request,
        io.grpc.stub.StreamObserver<calcstubs.Result> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getAddMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * generate the number powers with exponents betwwen 1 and maximum 
     * </pre>
     */
    public void generatePowers(calcstubs.NumberAndMaxExponent request,
        io.grpc.stub.StreamObserver<calcstubs.Result> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getGeneratePowersMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * add a sequence of numbers, ex: 1,2, 10, 5 = 18
     * </pre>
     */
    public io.grpc.stub.StreamObserver<calcstubs.Number> addSeqOfNumbers(
        io.grpc.stub.StreamObserver<calcstubs.Result> responseObserver) {
      return io.grpc.stub.ClientCalls.asyncClientStreamingCall(
          getChannel().newCall(getAddSeqOfNumbersMethod(), getCallOptions()), responseObserver);
    }

    /**
     * <pre>
     * Multiple add operations using a bidirecional stream
     * </pre>
     */
    public io.grpc.stub.StreamObserver<calcstubs.AddOperands> multipleAdd(
        io.grpc.stub.StreamObserver<calcstubs.Result> responseObserver) {
      return io.grpc.stub.ClientCalls.asyncBidiStreamingCall(
          getChannel().newCall(getMultipleAddMethod(), getCallOptions()), responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service CalcService.
   * <pre>
   * serviço com operações sobre números
   * </pre>
   */
  public static final class CalcServiceBlockingV2Stub
      extends io.grpc.stub.AbstractBlockingStub<CalcServiceBlockingV2Stub> {
    private CalcServiceBlockingV2Stub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CalcServiceBlockingV2Stub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CalcServiceBlockingV2Stub(channel, callOptions);
    }

    /**
     * <pre>
     * add two numbers
     * </pre>
     */
    public calcstubs.Result add(calcstubs.AddOperands request) throws io.grpc.StatusException {
      return io.grpc.stub.ClientCalls.blockingV2UnaryCall(
          getChannel(), getAddMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * generate the number powers with exponents betwwen 1 and maximum 
     * </pre>
     */
    @io.grpc.ExperimentalApi("https://github.com/grpc/grpc-java/issues/10918")
    public io.grpc.stub.BlockingClientCall<?, calcstubs.Result>
        generatePowers(calcstubs.NumberAndMaxExponent request) {
      return io.grpc.stub.ClientCalls.blockingV2ServerStreamingCall(
          getChannel(), getGeneratePowersMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * add a sequence of numbers, ex: 1,2, 10, 5 = 18
     * </pre>
     */
    @io.grpc.ExperimentalApi("https://github.com/grpc/grpc-java/issues/10918")
    public io.grpc.stub.BlockingClientCall<calcstubs.Number, calcstubs.Result>
        addSeqOfNumbers() {
      return io.grpc.stub.ClientCalls.blockingClientStreamingCall(
          getChannel(), getAddSeqOfNumbersMethod(), getCallOptions());
    }

    /**
     * <pre>
     * Multiple add operations using a bidirecional stream
     * </pre>
     */
    @io.grpc.ExperimentalApi("https://github.com/grpc/grpc-java/issues/10918")
    public io.grpc.stub.BlockingClientCall<calcstubs.AddOperands, calcstubs.Result>
        multipleAdd() {
      return io.grpc.stub.ClientCalls.blockingBidiStreamingCall(
          getChannel(), getMultipleAddMethod(), getCallOptions());
    }
  }

  /**
   * A stub to allow clients to do limited synchronous rpc calls to service CalcService.
   * <pre>
   * serviço com operações sobre números
   * </pre>
   */
  public static final class CalcServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<CalcServiceBlockingStub> {
    private CalcServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CalcServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CalcServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * add two numbers
     * </pre>
     */
    public calcstubs.Result add(calcstubs.AddOperands request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getAddMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * generate the number powers with exponents betwwen 1 and maximum 
     * </pre>
     */
    public java.util.Iterator<calcstubs.Result> generatePowers(
        calcstubs.NumberAndMaxExponent request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getGeneratePowersMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service CalcService.
   * <pre>
   * serviço com operações sobre números
   * </pre>
   */
  public static final class CalcServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<CalcServiceFutureStub> {
    private CalcServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected CalcServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new CalcServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * add two numbers
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<calcstubs.Result> add(
        calcstubs.AddOperands request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getAddMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_ADD = 0;
  private static final int METHODID_GENERATE_POWERS = 1;
  private static final int METHODID_ADD_SEQ_OF_NUMBERS = 2;
  private static final int METHODID_MULTIPLE_ADD = 3;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final AsyncService serviceImpl;
    private final int methodId;

    MethodHandlers(AsyncService serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_ADD:
          serviceImpl.add((calcstubs.AddOperands) request,
              (io.grpc.stub.StreamObserver<calcstubs.Result>) responseObserver);
          break;
        case METHODID_GENERATE_POWERS:
          serviceImpl.generatePowers((calcstubs.NumberAndMaxExponent) request,
              (io.grpc.stub.StreamObserver<calcstubs.Result>) responseObserver);
          break;
        default:
          throw new AssertionError();
      }
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public io.grpc.stub.StreamObserver<Req> invoke(
        io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_ADD_SEQ_OF_NUMBERS:
          return (io.grpc.stub.StreamObserver<Req>) serviceImpl.addSeqOfNumbers(
              (io.grpc.stub.StreamObserver<calcstubs.Result>) responseObserver);
        case METHODID_MULTIPLE_ADD:
          return (io.grpc.stub.StreamObserver<Req>) serviceImpl.multipleAdd(
              (io.grpc.stub.StreamObserver<calcstubs.Result>) responseObserver);
        default:
          throw new AssertionError();
      }
    }
  }

  public static final io.grpc.ServerServiceDefinition bindService(AsyncService service) {
    return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
        .addMethod(
          getAddMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              calcstubs.AddOperands,
              calcstubs.Result>(
                service, METHODID_ADD)))
        .addMethod(
          getGeneratePowersMethod(),
          io.grpc.stub.ServerCalls.asyncServerStreamingCall(
            new MethodHandlers<
              calcstubs.NumberAndMaxExponent,
              calcstubs.Result>(
                service, METHODID_GENERATE_POWERS)))
        .addMethod(
          getAddSeqOfNumbersMethod(),
          io.grpc.stub.ServerCalls.asyncClientStreamingCall(
            new MethodHandlers<
              calcstubs.Number,
              calcstubs.Result>(
                service, METHODID_ADD_SEQ_OF_NUMBERS)))
        .addMethod(
          getMultipleAddMethod(),
          io.grpc.stub.ServerCalls.asyncBidiStreamingCall(
            new MethodHandlers<
              calcstubs.AddOperands,
              calcstubs.Result>(
                service, METHODID_MULTIPLE_ADD)))
        .build();
  }

  private static abstract class CalcServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    CalcServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return calcstubs.CalcServiceOuterClass.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("CalcService");
    }
  }

  private static final class CalcServiceFileDescriptorSupplier
      extends CalcServiceBaseDescriptorSupplier {
    CalcServiceFileDescriptorSupplier() {}
  }

  private static final class CalcServiceMethodDescriptorSupplier
      extends CalcServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    CalcServiceMethodDescriptorSupplier(java.lang.String methodName) {
      this.methodName = methodName;
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.MethodDescriptor getMethodDescriptor() {
      return getServiceDescriptor().findMethodByName(methodName);
    }
  }

  private static volatile io.grpc.ServiceDescriptor serviceDescriptor;

  public static io.grpc.ServiceDescriptor getServiceDescriptor() {
    io.grpc.ServiceDescriptor result = serviceDescriptor;
    if (result == null) {
      synchronized (CalcServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new CalcServiceFileDescriptorSupplier())
              .addMethod(getAddMethod())
              .addMethod(getGeneratePowersMethod())
              .addMethod(getAddSeqOfNumbersMethod())
              .addMethod(getMultipleAddMethod())
              .build();
        }
      }
    }
    return result;
  }
}
