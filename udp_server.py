#!/usr/bin/env python3

import socket
import time


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 15000))

    while True:
        msg, addr = sock.recvfrom(8194)
        sock.sendto(msg * 10, addr)


if __name__ == '__main__':
    main()
