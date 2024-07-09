import grpc
import streamint_pb2
import streamint_pb2_grpc

def run():
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = streamint_pb2_grpc.StreamIntServiceStub(channel)
            response_iterator = stub.StreamInt(streamint_pb2.StreamIntRequest())
            for response in response_iterator:
                print(f"Received: {response.result}, {response.received}")
    except grpc.RpcError as e:
        print(f"RPC error: {e.code()}")
        print(f"Details: {e.details()}")

if __name__ == '__main__':
    run()