import socket
import threading
import secrets
import json
from   Request  import *
from   Response import *
from   Player   import *

class ServerUDP:
    def __init__(self) -> None:
        self.udpAddressPort    = ('127.0.0.1', 20001)
        self.tcpAddressPort = ('127.0.0.1', 20005)

        self.bufferSize      = 1024

        self.allRooms        = {}

        # instancia do servidor UDP
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind(self.udpAddressPort)

        # instancia do servidor TCP
        self.TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCPServerSocket.bind(self.tcpAddressPort)
        self.TCPServerSocket.listen()

        self.TCPconnections = [] # conexoes TCP 

        # dicionario com os enderecos TCP e UDP respectivos ao mesmo cliente
        self.TCPTOUDP       = {} 
        
    # retorna o correspondente endereco UDP com base no endereco TCP de um cliente
    def fromTcpToUdp(self, tcpaddress):
        if tcpaddress in self.TCPTOUDP:
            return self.TCPTOUDP[tcpaddress]
        return None
        
    # Recebe conexao UDP
    def getUDPRequest(self):
        try:
            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            clientMessageArray = json.loads(bytesAddressPair[0]) # dados enviados na requisicao
            clientMessageArray['address'] =  bytesAddressPair[1] # endereco do cliente
            request = Request()

            return request.createRequestFromArray(clientMessageArray)
        except:
            return False
    
    # Recebe conexao TCP
    def getTCPRequest(self):
        try:
            # objeto conexao TCP, e (endereco, porta)
            conn, addr = self.TCPServerSocket.accept()
            clientMessageArray = json.loads(conn.recv(self.bufferSize))
            clientMessageArray['address'] =  addr
            clientMessageArray['connection'] = conn

            request = Request()

            return request.createRequestFromArray(clientMessageArray)
        except:
            return False

    # envia resposta para uma conexao UDP
    def sendReponseWithUDP(self, response, address):
        # cria um JSON com base na Resposta, e entao transforma em uma string
        bytesToSend = str.encode(json.dumps(response.getResponseAsArray()))
        self.UDPServerSocket.sendto(bytesToSend, address)

    # envia resposta para uma conexao TCP
    def sendReponseWithTCP(self, response, connection):
        # cria um JSON com base na Resposta, e entao transforma em uma string
        bytesToSend = str.encode(json.dumps(response.getResponseAsArray()))
        connection.sendall(bytesToSend)

    # Pega os dados da conexao de um cliente TCP
    def getConnectionData(self, request):   
        # Dados enviados como JSON eh convertido para dicionario
        clientMessageArray = json.loads(request.getConnection().recv(self.bufferSize))

        # eh criado uma instancia da classe Request
        # com os dados enviados pelo cliente
        if 'token' in clientMessageArray:
            token = clientMessageArray['token']
        else:
            token = request.getToken()
        
        if 'requestCode' in clientMessageArray:
            requestCode = clientMessageArray['requestCode']
        else:
            requestCode = None
        
        if 'requestData' in clientMessageArray:
            requestData = clientMessageArray['requestData']
        else:
            requestData = None

        # a instancia da classe eh retornada para ser manipulada
        newRequest = Request(requestCode=requestCode, address=request.getAddress(), connection=request.getConnection(), token=token, requestData=requestData)

        return newRequest

    # criar nova sala no jogo
    def createNewRoom(self):
        token = secrets.token_hex(nbytes=16) # hash de 16 bytes 

        # eh criada uma sala inicializada sem jogadores, e sem vencedores
        self.allRooms[token] = {'users': {},
                                'winners': []
                               }

        return token
    
    # adiciona um usuario a uma sala ja existente
    def addUserToRoom(self, token, userAddress, playerConnection):
        if not (token in self.allRooms): # caso a sala nao exista
            return False
        
        room = self.allRooms[token] # dados da sala com base no seu token
        users = room['users']       # retorna todos os usuarios da sala

        # se a sala ja tiver 3 jogadores, entao ela esta cheia
        if len(users) >= 3:
            return False
        
        # se o usuario ja estiver na sala
        elif userAddress in users:
            return False
        
        else:
            if len(users) == 0:   # primeiro jogador
                x = 190
            elif len(users) == 1: # segundo jogador
                x = 400
            else:                 # terceiro jogador
                x = 610 

            # eh armazenada a instancia do Player na sala
            users[userAddress] = Player(playerId=userAddress, playerConnection=playerConnection, x=x)

            return users

    # retorna todas as conexoes TCP
    def getTCPConnections(self):
        return self.TCPconnections
    
    # retorna todas as salas
    def getAllRooms(self):
        return self.allRooms
    
    # retorna todos os jogadores de uma sala
    def getRoomUsers(self, token):
        if token in self.allRooms:
            return self.allRooms[token]['users']
        
        return False
    
    # retorna o(s) vencedor(es) de uma sala
    def getRoomWinners(self, token):
        if token in self.allRooms:
            return self.allRooms[token]['winners']
        
        return False

    # servidor UDP
    def udpServer(self):
        while True:
            # Recebe uma conexao UDP
            request = self.getUDPRequest()

            # Inicia uma thread para manipular as conexoes UDP
            newThread = threading.Thread(target=self.handleUDPRequest, args=(request,))
            newThread.start()
    
    # servidor TCP
    def tcpServer(self):
        while True:
            # Recebe uma conexao 
            request = self.getTCPRequest()

            # Inicia uma thread para manipular as conexoes TCP
            newThread = threading.Thread(target=self.handleTCPRequest, args=(request,))
            newThread.start()

    # metodo que inicia o servidor de fato, e fica ouvindo por
    # ambas conexoes UDP e TCP
    def startServer(self):
        # criando uma thread para manipular o servidor UDP
        udpThread = threading.Thread(target=self.udpServer)
        udpThread.start()

        # e outra para manipular o servidor TCP
        tcpThread = threading.Thread(target=self.tcpServer)
        tcpThread.start()
        
        print('Server is running')
    
    # metodo que manipula as conexoes TCP
    def handleTCPRequest(self, request):
        firstRequest=True

        while True:
            if not firstRequest == True:
                request = self.getConnectionData(request=request)
            
            if request:
                firstRequest = False
                if request.getRequestCode() == 100:
                    newRoomToken = self.createNewRoom()

                    response = Response(responseCode=201, token=newRoomToken)
                    self.sendReponseWithTCP(response, request.getConnection())

                # User listing rooms
                elif request.getRequestCode() == 103:
                    returnData = []
                    for room in self.getAllRooms():
                        returnData.append(room)

                    response = Response(responseCode=200, returnData=returnData)
                    self.sendReponseWithTCP(response, request.getConnection())
                
                # User is joining a room
                elif request.getRequestCode() == 101:
                    token = request.getToken()
                    clientUdpAddr = (request.getRequestData()[0], request.getRequestData()[1])
                    usersInRoom = self.addUserToRoom(token=token, userAddress=request.getAddress(), playerConnection=request.getConnection())

                    if not usersInRoom:
                        response = Response(responseCode=400)
                        self.sendReponseWithTCP(response, request.getConnection())
                    else:
                        self.TCPTOUDP[request.getAddress()] = clientUdpAddr

                        returnData = {}
                        returnData['message'] = '{} entrou na sala. {}/3'.format(request.getAddress(), len(usersInRoom))
                        returnData['playerInfo'] = usersInRoom[request.getAddress()].getPlayerAsArray()
                        for address in usersInRoom:
                            response = Response(responseCode=202, returnData=returnData)
                            self.sendReponseWithTCP(response, usersInRoom[address].getConnection())

                        if len(usersInRoom) >= 3:
                            returnData = {}
                            returnData['message'] = 'Partida pronta. {}/3'.format(len(usersInRoom))
                            returnData['players'] = []
                            for address in usersInRoom:
                                returnData['players'].append(usersInRoom[address].getPlayerAsArray())
                            for address in usersInRoom:
                                response = Response(responseCode=203, returnData=returnData)
                                self.sendReponseWithTCP(response, usersInRoom[address].getConnection())

    # metodo que manipula as conexoes UDP
    def handleUDPRequest(self, request):
        requestData = request.getRequestData()
        requestData['tcpAddress'] = (requestData['tcpAddress'][0], requestData['tcpAddress'][1])

        # User is already in a room
        if request.getRequestCode() == 102:
            token = request.getToken()
            usersInRoom = self.getRoomUsers(token=token)
            roomWinners = self.getRoomWinners(token=token)

            if not usersInRoom:
                print('1')
                response = Response(responseCode=400)
                self.sendReponseWithUDP(response, self.fromTcpToUdp(requestData['tcpAddress']))
            elif not (requestData['tcpAddress'] in usersInRoom):
                print(requestData['tcpAddress'])
                print('2')
                response = Response(responseCode=400)
                self.sendReponseWithUDP(response, self.fromTcpToUdp(requestData['tcpAddress']))
            elif requestData['tcpAddress'] in roomWinners:
                returnData = 'Voce ficou em {} lugar'.format(roomWinners.index(requestData['tcpAddress']) + 1)
                response = Response(responseCode=207, returnData=returnData)
                self.sendReponseWithUDP(response, self.fromTcpToUdp(requestData['tcpAddress']))
            elif requestData['pressedKey'] == 'a':
                for player in usersInRoom:
                    if usersInRoom[player].getPlayerId() == requestData['tcpAddress']:
                        playerObject = usersInRoom[player]
                        break

                playerObject.incrementY()

                if playerObject.getMap() >= 6:
                    roomWinners.append(requestData['tcpAddress'])
                    returnData = '{} ficou em {} lugar'.format(requestData['tcpAddress'], roomWinners.index(requestData['tcpAddress']) + 1)
                    response = Response(responseCode=206, returnData=returnData)
                else:
                    returnData = playerObject.getPlayerAsArray()
                    response = Response(responseCode=205, returnData=returnData)

                for user in usersInRoom:
                    # Sending a reply to client
                    self.sendReponseWithUDP(response, self.fromTcpToUdp(user))
                
                if len(roomWinners) >= 3:
                    self.allRooms.pop(token)
                    for user in usersInRoom:
                        returnData = 'A partida acabou'
                        response = Response(responseCode=210, returnData=returnData)
                        self.sendReponseWithUDP(response, self.fromTcpToUdp(user))
            else:
                print('3')
                response = Response(responseCode=400)
                self.sendReponseWithUDP(response, self.fromTcpToUdp(user))
