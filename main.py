"""Runs main python server for MOSS"""

import argparse
from openbci import OpenBCICyton


def print_raw(sample):
    """
    Prints the raw data from the OpenBCI Cyton board
    """
    print(sample.channels_data)


def main():
    """
    Main function to run the OpenBCI Cyton board connection
    """
    parser = argparse.ArgumentParser(
        description='OpenBCI Cyton Board Connection')
    parser.add_argument('--port', type=str, required=True,
                        help='The port to connect to the OpenBCI Cyton board')

    args = parser.parse_args()

    board = OpenBCICyton(port=args.port, daisy=False)
    board.start_stream(print_raw)


if __name__ == '__main__':
    main()
