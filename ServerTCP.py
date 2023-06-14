import socket
import threading

HOST = '192.168.0.6'
PORT = 55556
bufferSize = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # servidor TCP
server.bind((HOST, PORT))
server.listen()

clients = [] 
nicknames = [] # nome dos clientes

# enviando a mensagem para todos os clientes
def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        # fica ouvindo por mensagens enviadas ao servidor, e repassa ela para todos os clientes
        try:
            message = client.recv(bufferSize)
            broadcast(message)

        # caso haja algum erro, o cliente eh removido do bate-papo 
        # ele eh removido, e uma msg eh enviada para todos na sala
        except:
            index = client.index(client)
            clients.remove(index)
            client.close() # fecha a conexao TCP com o cliente

            nickname = nicknames[index]
            broadcast(f'{nickname} saiu do chat!'.encode('ascii'))
            nicknames.remove(nickname)

            break

def receive():
    while True:
        client, address = server.accept() # se o cliente conseguiu se conectar, pega os dados dele
        print(f'{client} conectou com o endereço {str(address)}')

        # NICK representa que o servidor esta aguardando que o cliente envie o seu nome no jogo
        client.send('_NICK'.encode('ascii'))
        nickname = client.recv(bufferSize).decode('ascii')

        # adicionar o cliente a lista de clientes e seu respectivo nickname (apelido no jogo)
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname do cliente é: {nickname}')
        broadcast(f'{nickname} entrou na partida'.encode('ascii'))
        
        client.send('Conectado a partida'.encode('ascii'))

        # iniciar uma thread encarregada de ficar ouvindo todas as msg que o novo cliente enviar
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print('Servidor está rodando...')
receive()