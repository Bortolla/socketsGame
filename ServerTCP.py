import socket
import threading
from Request import * 
from Response import *

class ServerTCP:
    def __init__(self) -> None:
        self.localIP = "127.0.0.1"
        self.localPort = 20001
        self.bufferSize = 1024 
        
        self.clients = []
        self.nicknames = []

        self.TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCPServerSocket.bind((self.localIP, self.localPort))
        self.TCPServerSocket.listen()

    # enviando a mensagem para todos os clientes
    def broadcast(self, message):
        try:
            for client in self.clients:
                client.send(message)
        except:
            print('Houve um erro no método broadcast ServerTCP')

    def handle(self, client):
        while True:
            # fica ouvindo por mensagens enviadas ao servidor, e repassa ela para todos os clientes
            try:
                message = client.recv(self.bufferSize)
                self.broadcast(message)

            # caso haja algum erro, o cliente eh removido do bate-papo 
            # ele eh removido, e uma msg eh enviada para todos na sala
            except:
                index = client.index(client)
                self.clients.remove(index)
                client.close() # fecha a conexao TCP com o cliente

                nickname = self.nicknames[index]
                self.broadcast(f'{nickname} saiu do chat!'.encode('ascii'))
                self.nicknames.remove(nickname)

                break

    def receive(self):
        while True:
            client, address = self.TCPServerSocket.accept() # se o cliente conseguiu se conectar, pega os dados dele
            print(f'{client} conectou com o endereço {str(address)}')

            # NICK representa que o servidor esta aguardando que o cliente envie o seu nome no jogo
            client.send('_NICK'.encode('ascii'))
            nickname = client.recv(self.bufferSize).decode('ascii')

            # adicionar o cliente a lista de clientes e seu respectivo nickname (apelido no jogo)
            self.nicknames.append(nickname)
            self.clients.append(client)

            print(f'Nickname do cliente é: {nickname}\n')
            self.broadcast(f'{nickname} entrou na partida\n'.encode('ascii'))
            
            client.send('Conectado a partida'.encode('ascii'))

            # iniciar uma thread encarregada de ficar ouvindo todas as msg que o novo cliente enviar
            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()

# Desktop/trabalhoRedes/socketsGame

server = ServerTCP()
print('Servidor está rodando')
server.receive()

# print('Servidor está rodando...')
# receive()