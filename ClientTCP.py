import socket
import threading

class ClientTCP:
    def __init__(self) -> None:
        self.localIP = "127.0.0.1"
        self.localPort = 20001
        self.bufferSize = 1024 

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.localIP, self.localPort))

        self.nickname = input('Escolha um nickname (apelido) na partida: ')

    def receive(self) -> None:
        while True:
            try:
                message = self.client.recv(self.bufferSize).decode('ascii')

                # cliente esta enviando o seu nickname (apelido) na partida
                if (message == '_NICK'):
                    self.client.send(self.nickname.encode('ascii'))

                else:
                    print(message)

            except: 
                print('Erro na função receive ClientTCP')
                self.client.close() # fecha conexao TCP
                break

    def write(self):
        while True:
            message = f'{self.nickname}: {input("")}'
            self.client.send(message.encode('ascii')) # envia a mensagem para o servidor


client = ClientTCP()

receive_thread = threading.Thread(target=client.receive)
receive_thread.start()

write_thread = threading.Thread(target=client.write)
write_thread.start()