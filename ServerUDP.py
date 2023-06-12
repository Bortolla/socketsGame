import socket
import threading
import secrets # biblioteca para criar um token único para as salas
import json    # biblioteca para codificar e decodificar objetos do tipo JSON
from   Request  import *
from   Response import *
from   Player   import *

# Classe para manipular um socket com uma instancia de conexao do tipo UDP
class ServerUDP:
    def __init__(self) -> None:
        self.localIP         = "127.0.0.1" 
        self.localPort       = 20001 
        self.bufferSize      = 1024 # tamanho dos dados enviados em bytes
        self.allRooms        = {}   # Todas as salas criadas no jogo, ativas ou nao ativass
        self.ongoingMatches  = {}   # dicionario com todas as salas em que as partidas estao ativas
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # criando uma conexao UDP
        self.UDPServerSocket.bind((self.localIP, self.localPort))

    def getRequest(self):
        try:
            # Recebe o pacote do cliente juntamente com seu endereço
            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            clientMessageArray = json.loads(bytesAddressPair[0]) # Transforma JSON em dicionario Python
            clientMessageArray['address'] =  bytesAddressPair[1] 

            # Retorna uma instancia da classe Request passando como parametro os dados do cliente
            request = Request()
            return request.createRequestFromArray(clientMessageArray)
        
        except:
            return False
        
    def sendResponse(self, response, address):
        # Transforma o dicionario de resposta em um JSON, e entao transforma o JSON em uma string
        bytesToSend = str.encode(json.dumps(response.getResponseAsArray())) 
        # a resposta eh enviada para o cliente no seu respectivo endereco
        self.UDPServerSocket.sendto(bytesToSend, address)

    def createNewRoom(self):
        # um token de tamanho de 16 bytes eh gerado aleatoriamente
        token = secrets.token_hex(nbytes=16)

        # eh adicionada uma sala ao vetor allRooms com o token gerado
        self.allRooms[token] = {'users': {},
                                'winners': []
                               }

        return token
    
    def addUserToRoom(self, token, userAddress):
        # caso a sala nao exista
        if not (token in self.allRooms):
            return False
        
        room = self.allRooms[token]
        users = room['users']

        # se a sala tiver 3 ou mais participantes, ninguem mais pode entrar
        if len(users) >= 3:
            return False
        
        # se o usuario ja estiver na sala, ele nao pode entrar novamente
        elif userAddress in users:
            return False

        # o usuario eh inserido, caso a sala nao esteja cheia e ele ainda nao esteja na sala
        else:
            if len(users) == 0:
                x = 190 # primeiro a entrar inicia com a posicao 190
            elif len(users) == 1:
                x = 400 # segundo a entrar inicia com a posicao 400
            else:
                x = 610 # terceiro a entrar inicia com a posicao 610
            users[userAddress] = Player(playerId=userAddress, x=x) # o usuario eh adicionado no vetor de usuarios

            return users

    # retorna todos os usuarios da sala com base no seu token
    def getRoomUsers(self, token):
        if token in self.allRooms:
            return self.allRooms[token]['users']
        
        return False
    
    # retorna o vencedor da sala com base no seu token
    def getRoomWinners(self, token):
        if token in self.allRooms:
            return self.allRooms[token]['winners']
        
        return False

    # Inicia o servidor UDP                 
    def startUDPServer(self):
        print('UDP server is running')
        
        # fica ouvindo por conexoes
        while True:
            request = self.getRequest()

            # Inicia nova thread e passa o handler da instancia da classe Request para manipular a nova conexao
            newThread = threading.Thread(target=self.handleRequest, args=(request,))  
            newThread.start()
            
    def handleRequest(self, request):
        # User is creating a new room
        if request.getRequestCode() == 100:
            newRoomToken = self.createNewRoom() # token da sala criada

            response = Response(responseCode=201, token=newRoomToken) # resposta com codigo de sucesso e token
            self.sendResponse(response, request.getAddress())
        
        # User is joining a room
        elif request.getRequestCode() == 101:
            token = request.getToken() # token da sala passada na requisicao
            usersInRoom = self.addUserToRoom(token=token, userAddress=request.getAddress()) 

            # caso o usuario nao tenha sido inserido na sala, eh retornada uma resposta de bad request
            if not usersInRoom: 
                response = Response(responseCode=400)
                self.sendResponse(response, request.getAddress())
            else:
                returnData = {}
                returnData['message'] = '{} entrou na sala. {}/3'.format(request.getAddress(), len(usersInRoom))
                returnData['playerInfo'] = usersInRoom[request.getAddress()].getPlayerAsArray()
                for addressKey in usersInRoom:
                    response = Response(responseCode=202, returnData=returnData)
                    self.sendResponse(response, addressKey)

                if len(usersInRoom) >= 3:
                    returnData = {}
                    returnData['message'] = 'Partida pronta. {}/3'.format(len(usersInRoom))
                    returnData['players'] = []
                    for player in usersInRoom:
                        returnData['players'].append(usersInRoom[player].getPlayerAsArray())
                    for addressKey in usersInRoom:
                        response = Response(responseCode=203, returnData=returnData)
                        self.sendResponse(response, addressKey)

        # User is already in a room
        elif request.getRequestCode() == 102:
            requestData = request.getRequestData()
            token = request.getToken()
            usersInRoom = self.getRoomUsers(token=token)
            roomWinners = self.getRoomWinners(token=token)

            if not usersInRoom:
                response = Response(responseCode=400)
                self.sendResponse(response, request.getAddress())
            elif not (request.getAddress() in usersInRoom):
                response = Response(responseCode=400)
                self.sendResponse(response, request.getAddress())
            elif request.getAddress() in roomWinners:
                returnData = 'Voce ficou em {} lugar'.format(roomWinners.index(request.getAddress()) + 1)
                response = Response(responseCode=207, returnData=returnData)
                self.sendResponse(response, request.getAddress())
            elif requestData['pressedKey'] == 'a':
                for player in usersInRoom:
                    if usersInRoom[player].getPlayerId() == request.getAddress():
                        playerObject = usersInRoom[player]
                        break

                playerObject.incrementY()

                if playerObject.getMap() >= 6:
                    roomWinners.append(request.getAddress())
                    returnData = '{} ficou em {} lugar'.format(request.getAddress(), roomWinners.index(request.getAddress()) + 1)
                    response = Response(responseCode=206, returnData=returnData)
                else:
                    returnData = playerObject.getPlayerAsArray()
                    response = Response(responseCode=205, returnData=returnData)

                for user in usersInRoom:
                    # Sending a reply to client
                    self.sendResponse(response, user)
                
                if len(roomWinners) >= 3:
                    self.allRooms.pop(token)
                    for user in usersInRoom:
                        returnData = 'A partida acabou'
                        response = Response(responseCode=210, returnData=returnData)
                        self.sendResponse(response, user)
            else:
                response = Response(responseCode=400)
                self.sendResponse(response, request.getAddress())