#!/usr/bin/env python3.5

import socket
import select


class TCPServer:
    def __init__(self, client_handler, handler_list):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', 15000))
        self.sock.listen(1)
        self.client_handler = client_handler
        self.handler_list = handler_list

    def fileno(self):
        return(self.sock.fileno())

    def ready_to_receive(self):
        return(True)

    def ready_to_send(self):
        return(False)

    def handle_receive(self):
        client, addr = self.sock.accept()
        print('Accept client: {}'.format(client))
        self.handler_list.append(self.client_handler(client, self.handler_list))


class TCPClient:
    def __init__(self, sock, handler_list):
        self.sock = sock
        self.handler_list = handler_list
        self.outgoing = bytearray()

    def fileno(self):
        return(self.sock.fileno())

    def close(self):
        self.sock.close()
        self.handler_list.remove(self)

    def ready_to_send(self):
        return(True if self.outgoing else False)

    def handle_send(self):
        nsent = self.sock.send(self.outgoing)
        print('nsent: {}'.format(nsent))
        self.outgoing = self.outgoing[nsent:]

    def ready_to_receive(self):
        return(True)

    def handle_receive(self):
        data = self.sock.recv(8192)
        print(data)
        if not data:
            print('close')
            self.close()
        else:
            self.outgoing.extend(data)


def event_loop(handlers):
    while True:
        receivers = [h for h in handlers if h.ready_to_receive]
        senders = [h for h in handlers if h.ready_to_send]
        can_receive, can_send, _ = select.select(receivers, senders, [])
        for r in can_receive:
            r.handle_receive()
        for s in can_send:
            s.handle_send()

if __name__ == '__main__':
    handlers = []
    handlers.append(TCPServer(TCPClient, handlers))
    event_loop(handlers)
