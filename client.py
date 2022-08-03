import socket
from threading import Thread


def get_port() -> int:
    with open('port.txt') as f:
        return int(f.read())


client = socket.socket()

client.connect(('localhost', get_port()))

name = input('Enter your name: ')
client.send(name.encode())

_close = False


def send():
    global _close
    while True:
        msg = input()
        if msg == '/exit':
            _close = True
            client.send(msg.encode())
            break
        client.send(msg.encode())


def receive():
    global _close
    while True:
        if _close:
            close()
            break

        print(client.recv(1024).decode())


def close():
    msg = '/exit'
    client.send(msg.encode())
    client.close()


Thread(target=send).start()
Thread(target=receive).start()
