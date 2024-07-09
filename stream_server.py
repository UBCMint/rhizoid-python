import signal
import threading
import time
from concurrent import futures

import serial

import grpc
import streamint_pb2 as pb2
import streamint_pb2_grpc as pb2_grpc
from openbci import OpenBCICyton

# Global variables
LATEST_DATA = None
DATA_LOCK = threading.Lock()
STOP_EVENT = threading.Event()
SERVER = None
BOARD = None


def signal_handler():
    print("\nCtrl+C pressed. Stopping the server and Bluetooth connection...")
    STOP_EVENT.set()
    if SERVER:
        SERVER.stop(0)
    if BOARD:
        BOARD.stop_stream()


signal.signal(signal.SIGINT, signal_handler)


def run_bluetooth():
    global BOARD
    try:
        print("Attempting to connect to OpenBCI board...")
        BOARD = OpenBCICyton(port="COM8", daisy=False)
        print("Connected to OpenBCI board. Starting stream...")
        BOARD.start_stream(update_data)
        while not STOP_EVENT.is_set():
            time.sleep(0.1)
    except serial.serialutil.SerialException as e:
        print(f"Error connecting to OpenBCI board: {e}")
    except Exception as e:
        print(f"Unexpected error in run_bluetooth: {e}")
    finally:
        if BOARD:
            BOARD.stop_stream()
            BOARD.disconnect()
        print("Bluetooth connection closed.")


class StreamService(pb2_grpc.StreamIntServiceServicer):
    def StreamInt(self, request, context):
        print("StreamInt method called")
        while not STOP_EVENT.is_set():
            with DATA_LOCK:
                if LATEST_DATA is not None:
                    result = int(LATEST_DATA[0])
                    received = True
                    print(f"Sending: result={result}, received={received}")
                    yield pb2.StreamIntResponse(result=result, received=received)
                else:
                    print("Waiting for data...")
            time.sleep(0.1)


def update_data(sample):
    global LATEST_DATA
    with DATA_LOCK:
        LATEST_DATA = sample.channels_data
    print("Received data from OpenBCI:", LATEST_DATA)


def serve():
    global SERVER
    SERVER = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_StreamIntServiceServicer_to_server(StreamService(), SERVER)
    SERVER.add_insecure_port("[::]:50051")
    SERVER.start()
    print("Server started at port 50051")
    try:
        while not STOP_EVENT.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        SERVER.stop(0)
        print("gRPC server stopped.")


def main():
    print("Starting Bluetooth thread...")
    bluetooth_thread = threading.Thread(target=run_bluetooth)
    bluetooth_thread.start()

    print("Starting gRPC server...")
    serve()

    bluetooth_thread.join()
    print("Main thread exiting.")


if __name__ == "__main__":
    main()
