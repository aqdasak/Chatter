from random import randint
import socket
from threading import Thread


clients = []
clients_names = []


def set_new_port() -> int:
    r = randint(9000, 65535)
    with open('port.txt', 'w') as f:
        f.write(str(r))
    print('Port:', r)
    return r


# chatting_with = []

def connect(server):
    while True:
        client, address = server.accept()
        name = client.recv(1024).decode().upper()
        if not name or not name.isprintable():
            name = 'USER_' + str(len(clients_names) + 1)
        print('Connected with', address, name)
        send_help(client)
        broadcast_from_server(name + ' is online')
        send_online_users(client)
        Thread(target=receive_message, args=(client, name)).start()
        clients.append(client)
        clients_names.append(name)


# This function runs in separate thread for each client
def receive_message(client, client_name):
    chatting_with = None
    while True:
        msg = client.recv(1024).decode()
        if msg.lower() == '/exit':
            remove_client(client)
            break
        elif msg.lower() == '/online':
            send_online_users(client)
        elif msg.lower() == '/help':
            send_help(client)
        elif msg.lower() == '/group':
            chatting_with = None
        elif msg[0] == '/' and msg[1:].isdigit():
            index = int(msg[1:]) - 1
            if index <= len(clients):
                chatting_with = clients[index]
                client.send(b'Message will be send to ' +
                            clients_names[index].encode())
            else:
                client.send(b'User not available')
        elif chatting_with:
            send_personal_message(client_name, chatting_with, msg)
        else:
            send_group_message(client, client_name, msg)


def send_personal_message(sender_name, send_to, message: str):
    msg = f'{sender_name}: {message}'
    msg = 'PRIVATE' + '_' * 33 + f'\n\t\t{msg}\n' + '_' * 40
    send_to.send(msg.encode())


def send_group_message(sender, sender_name, message: str):
    clients_copy = clients.copy()
    clients_copy.remove(sender)
    for client in clients_copy:
        msg = f'\t\t{sender_name}: {message}'
        client.send(msg.encode())


def send_help(send_to):
    message = '''HELP__________________________________________
/help    - show this help
/exit    - exit the chat
/online  - show list of online users
/(index) - privately chat with particular user
/group   - group chat with all online users
______________________________________________'''
    broadcast_from_server(message, broadcast_to=[send_to])


def broadcast_from_server(message: str, broadcast_to=clients):
    message = '>> ' + message.replace('\n', '\n>> ')
    for client in broadcast_to:
        client.send(message.encode())


def send_online_users(send_to: socket):
    if len(clients_names) == 0:
        return None
    msg = ''
    for index, name in enumerate(clients_names):
        msg += f'{index + 1}: {name}\n'
    msg = f'\n__ONLINE USERS__\n{msg}' + '_' * 16
    send_to.send(msg.encode())


def remove_client(client):
    index = clients.index(client)
    client.send(b'Exiting...')
    print('Disconnected with', clients_names[index])
    del clients[index]
    broadcast_from_server(clients_names[index] + ' is offline')
    del clients_names[index]


def main():
    server = socket.socket(socket.SO_REUSEADDR)
    print('Socket created')

    server.bind(('localhost', set_new_port()))
    server.listen()
    print('Waiting for connection')

    Thread(target=connect, args=(server,)).start()


if __name__ == '__main__':
    main()
