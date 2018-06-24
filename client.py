import socket
import time
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ


def get():
    global n_jobs
    n_jobs += 1
    s = socket.socket()
    s.setblocking(False)

    try:
        s.connect(('127.0.0.1', 50007))
    except BlockingIOError:
        pass

    callback = lambda: connected(s)
    selector.register(s.fileno(), EVENT_WRITE, callback)


def connected(s):
    selector.unregister(s.fileno())
    s.send(b'hello server')

    buf = []
    callback = lambda: readable(s, buf)
    selector.register(s.fileno(), EVENT_READ, callback)


def readable(s, buf):
    global n_jobs
    selector.unregister(s.fileno())
    chunk = s.recv(2)
    if chunk:
        buf.append(chunk)
        callback = lambda: readable(s, buf)
        selector.register(s.fileno(), EVENT_READ, callback)
    else:
        body = b''.join(buf)
        print(len(body))
        n_jobs -= 1

if __name__ == '__main__':
    selector = DefaultSelector()
    n_jobs = 0
    t = time.time()
    get()
    get()
    get()
    while n_jobs:
        events = selector.select()
        for key, mask in events:
            callback = key.data
            callback()

    print('{:.1f}'.format(time.time() - t))
