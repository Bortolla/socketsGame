import socket
import threading
import secrets
import json
from   Request  import *
from   Response import *
from   Player   import *

class ServerUDP:
    def __init__(self) -> None:
        self.udpAddressPort    = ('127.0.0.1', 20005)
        self.tcpAddressPort = ('127.0.0.1', 20005)

        self.bufferSize      = 1024

        self.allRooms        = {}

        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind(self.udpAddressPort)

        self.TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCPServerSocket.bind(self.tcpAddressPort)
        self.TCPServerSocket.listen()

        self.TCPconnections = []
        
    def getUDPRequest(self):
        try:
            # Reveives a new UDP connection
            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            clientMessageArray = json.loads(bytesAddressPair[0])
            clientMessageArray['address'] =  bytesAddressPair[1]

            request = Request()

            return request.createRequestFromArray(clientMessageArray)
        except:
            return False
        
    def getTCPRequest(self):
        try:
            conn, addr = self.TCPServerSocket.accept()
            clientMessageArray = json.loads(conn.recv(self.bufferSize))
            clientMessageArray['address'] =  addr
            clientMessageArray['connection'] = conn

            request = Request()

            return request.createRequestFromArray(clientMessageArray)
        except:
            return False

    def sendReponseWithUDP(self, response, address):
        bytesToSend = str.encode(json.dumps(response.getResponseAsArray()))
        self.UDPServerSocket.sendto(bytesToSend, address)

    def sendReponseWithTCP(self, response, connection):
        bytesToSend = str.encode(json.dumps(response.getResponseAsArray()))
        connection.sendall(bytesToSend)

    def getConnectionData(self, request):
        clientMessageArray = json.loads(request.getConnection().recv(self.bufferSize))

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

        newRequest = Request(requestCode=requestCode, address=request.getAddress(), connection=request.getConnection(), token=token, requestData=requestData)

        return newRequest

    def createNewRoom(self):
        token = secrets.token_hex(nbytes=16)

        self.allRooms[token] = {'users': {},
                                'winners': []
                               }

        return token
    
    def addUserToRoom(self, token, userAddress, playerConnection):
        if not (token in self.allRooms):
            return False
        
        room = self.allRooms[token]
        users = room['users']

        if len(users) >= 3:
            return False
        elif userAddress in users:
            return False
        else:
            if len(users) == 0:
                x = 190
            elif len(users) == 1:
                x = 400
            else:
                x = 610
            users[userAddress] = Player(playerId=userAddress, playerConnection=playerConnection, x=x)

            return users

    def getTCPConnections(self):
        return self.TCPconnections
    
    def getAllRooms(self):
        return self.allRooms
    
    def getRoomUsers(self, token):
        if token in self.allRooms:
            return self.allRooms[token]['users']
        
        return False
    
    def getRoomWinners(self, token):
        if token in self.allRooms:
            return self.allRooms[token]['winners']
        
        return False

    def udpServer(self):
        while True:
            # Reveives a new UDP connection
            request = self.getUDPRequest()
            # Starts thread to handle the connection
            newThread = threading.Thread(target=self.handleUDPRequest, args=(request,))
            newThread.start()
    
    def tcpServer(self):
        while True:
            # Reveives a new UDP connection
            request = self.getTCPRequest()
            # Starts thread to handle the connection
            newThread = threading.Thread(target=self.handleTCPRequest, args=(request,))
            newThread.start()

    def startServer(self):
        udpThread = threading.Thread(target=self.udpServer)
        udpThread.start()

        tcpThread = threading.Thread(target=self.tcpServer)
        tcpThread.start()
        
        print('Server is running')
            
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
                    usersInRoom = self.addUserToRoom(token=token, userAddress=request.getAddress(), playerConnection=request.getConnection())

                    if not usersInRoom:
                        response = Response(responseCode=400)
                        self.sendReponseWithTCP(response, request.getConnection())
                    else:
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

    def handleUDPRequest(self, request):
        print(self.allRooms)
        # User is already in a room
        if request.getRequestCode() == 102:
            requestData = request.getRequestData()
            token = request.getToken()
            usersInRoom = self.getRoomUsers(token=token)
            roomWinners = self.getRoomWinners(token=token)

            if not usersInRoom:
                print('1')
                response = Response(responseCode=400)
                self.sendReponseWithUDP(response, request.getAddress())
            elif not (request.getAddress() in usersInRoom):
                print(request.getAddress())
                print('2')
                response = Response(responseCode=400)
                self.sendReponseWithUDP(response, request.getAddress())
            elif request.getAddress() in roomWinners:
                returnData = 'Voce ficou em {} lugar'.format(roomWinners.index(request.getAddress()) + 1)
                response = Response(responseCode=207, returnData=returnData)
                self.sendReponseWithUDP(response, request.getAddress())
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
                    self.sendReponseWithUDP(response, user)
                
                if len(roomWinners) >= 3:
                    self.allRooms.pop(token)
                    for user in usersInRoom:
                        returnData = 'A partida acabou'
                        response = Response(responseCode=210, returnData=returnData)
                        self.sendReponseWithUDP(response, user)
            else:
                print('3')
                response = Response(responseCode=400)
                self.sendReponseWithUDP(response, request.getAddress())
