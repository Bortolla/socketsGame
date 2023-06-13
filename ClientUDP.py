import socket
import json                     # biblioteca para manipular dados no formato JSON
import queue                    # estrutura de dados fila
from   Request       import *   # classe Request
from   Response      import *   # classe Response
from   pygame.locals import *   # constantes da biblioteca pygame

class ClientUDP:
    def __init__(self) -> None:
        self.serverAddressPort = ('127.0.0.1', 20001) # endereco e porta do cliente
        self.bufferSize        = 1024 # tamanho max do buffer (dados a serem enviados)
        self.UDPClientSocket   = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)   # instancia UDP do socket para redes
        self.currentRoom       = None   # cliente inicia sem sala
        self.sharedQueue       = queue.Queue()  # fila dos clientes (jogadores)

    # Envia requisicao para o servidor com os dados do cliente 
    def sendRequest(self, request):
        bytesToSend = str.encode(json.dumps(request.getRequestAsArray()))
        self.UDPClientSocket.sendto(bytesToSend, self.serverAddressPort)
    
    # Pega a resposta do servidor
    def getResponse(self):
        try:
            # Pega a mensagem do servidor com tamanho max de 1024
            bytesAddressPair = self.UDPClientSocket.recvfrom(self.bufferSize)
            # pega somente a mensagem do servidor
            serverMessageArray = json.loads(bytesAddressPair[0]) 

            response = Response() 

            # retorna um dicionario a partir da resposta recebida
            return response.createResponseFromArray(serverMessageArray)
        except:
            return False # se nao retorna False, isto eh, algum erro ocorreu
    
    # Ficar pegando todas as respostas que o servidor enviou
    def getResponses(self):
        while True:
            response = self.getResponse()
            
            # Se houver uma resposta, colocar ela na fila de respostas
            if response:                   
                self.sharedQueue.put(response)

    def getQueue(self):
        return self.sharedQueue

    # realiza uma requisicao com o codigo do tipo 100 (criar sala)    
    def createRoom(self):
        request = Request(requestCode=100)
        self.sendRequest(request)

        # Retorna a resposta do servidor (objeto do tipo Response)
        return self.getResponse()

    # Requisitar para entrar em uma sala a partir do token
    def joinRoom(self, roomToken):
        self.currentRoom = roomToken

        request = Request(requestCode=101, token=self.currentRoom)
        self.sendRequest(request=request)

        # Retorna objeto do tipo Response (resposta do servidor)
        return self.getResponse()
