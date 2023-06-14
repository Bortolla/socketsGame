import socket
import threading

HOST = '192.168.0.6'
PORT = 55556
bufferSize = 1024 # tamanho das mensagens em Bytes

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

nickname = input('Escolha uma nickname (apelido) na partida: ')

def receive():
    while True:
        try:
            message = client.recv(bufferSize).decode('ascii')

            # cliente esta enviando o seu nickname (apelido) na partida
            if (message == '_NICK'):
                client.send(nickname.encode('ascii'))

            else:
                print(message)

        except: 
            print('Erro na função receive ClientTCP')
            client.close() # fecha conexao TCP
            break

def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode('ascii')) # envia a mensagem para o servidor

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()