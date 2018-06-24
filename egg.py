#!/usr/bin/env python3

import select
import socket


class TCPServer:
    def __init__(self, handle_client, handle_list):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', 15000))
        self.sock.listen(1)
        self.handle_client = handle_client
        self.handle_list = handle_list

    def fileno(self):
        return(self.sock.fileno())

    def ready_to_receive(self):
        return(True)

    def ready_to_send(self):
        return(False)

    def handle_receive(self):
        client, addr = self.sock.accept()
        print('Accept from: {}'.format(client))
        self.handle_list.append(self.handle_client(client, self.handle_list))


class TCPClient:
    def __init__(self, client, handle_list):
        self.sock = client
        self.handle_list = handle_list
        self.outgoing = bytearray()

    def fileno(self):
        return(self.sock.fileno())

    def close(self):
        self.sock.close()
        self.handle_list.remove(self)

    def ready_to_send(self):
        return(True if self.outgoing else False)

    def ready_to_receive(self):
        return(True)

    def handle_receive(self):
        data = self.sock.recv(128)
        if not data:
            self.close()
        else:
            self.outgoing.extend(data)

    def handle_send(self):
        nsent = self.sock.send(self.outgoing)
        self.outgoing = self.outgoing[nsent:]


def event_loop(handlers):
    while True:
        can_receivers = [h for h in handlers if h.ready_to_receive()]
        can_senders = [h for h in handlers if h.ready_to_send()]
        receivers, senders, _ = select.select(can_receivers, can_senders, [])
        for r in receivers:
            r.handle_receive()
        for s in senders:
            s.handle_send()

handlers = []
handlers.append(TCPServer(TCPClient, handlers))
event_loop(handlers)
