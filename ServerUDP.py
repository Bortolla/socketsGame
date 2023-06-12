import socket
import threading
import secrets
import json
from   Request  import *
from   Response import *
from   Player   import *

class ServerUDP:
    def __init__(self) -> None:
        self.localIP         = "127.0.0.1"
        self.localPort       = 20001
        self.bufferSize      = 1024
        self.allRooms        = {}
        self.ongoingMatches  = {}
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((self.localIP, self.localPort))

    def getRequest(self):
        try:
            # Reveives a new UDP connection
            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            clientMessageArray = json.loads(bytesAddressPair[0])
            clientMessageArray['address'] =  bytesAddressPair[1]

            request = Request()

            return request.createRequestFromArray(clientMessageArray)
        
        except:
            return False
        
    def sendResponse(self, response, address):
        # Sending response back
        bytesToSend = str.encode(json.dumps(response.getResponseAsArray()))
        self.UDPServerSocket.sendto(bytesToSend, address)

    def createNewRoom(self):
        token = secrets.token_hex(nbytes=16)

        self.allRooms[token] = {'users': {},
                                'winners': []
                               }

        return token
    
    def addUserToRoom(self, token, userAddress):
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
            users[userAddress] = Player(playerId=userAddress, x=x)

            return users

    def getRoomUsers(self, token):
        if token in self.allRooms:
            return self.allRooms[token]['users']
        
        return False
    
    def getRoomWinners(self, token):
        if token in self.allRooms:
            return self.allRooms[token]['winners']
        
        return False
                    

    def startUDPServer(self):
        print('UDP server is running')
        while True:

            # Reveives a new UDP connection
            request = self.getRequest()
            # Starts thread to handle the connection
            newThread = threading.Thread(target=self.handleRequest, args=(request,))
            newThread.start()
            
    def handleRequest(self, request):
        # User is creating a new room
        if request.getRequestCode() == 100:
            newRoomToken = self.createNewRoom()

            response = Response(responseCode=201, token=newRoomToken)
            self.sendResponse(response, request.getAddress())
        
        # User is joining a room
        elif request.getRequestCode() == 101:
            token = request.getToken()
            usersInRoom = self.addUserToRoom(token=token, userAddress=request.getAddress())

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