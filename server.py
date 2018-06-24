import socket

HOST = ''
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(10)
while True:
    conn, addr = s.accept()
    print('Connected by {}'.format(addr))
    while True:
        data = conn.recv(1024)
        conn.sendall(data*1024*10)
        conn.close()
        break

conn.close()
