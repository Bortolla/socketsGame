import socket
import json
import queue
from   Request       import *
from   Response      import *
from   pygame.locals import *

class ClientUDP:
    def __init__(self) -> None:
        self.serverAddressPort = ('127.0.0.1', 20001)
        self.bufferSize        = 1024
        self.UDPClientSocket   = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.currentRoom       = None
        self.sharedQueue       = queue.Queue()

    def sendRequest(self, request):
        # Sending UDP message to the server 
        bytesToSend = str.encode(json.dumps(request.getRequestAsArray()))
        self.UDPClientSocket.sendto(bytesToSend, self.serverAddressPort)
    
    def getResponse(self):
        try:
            # Waiting for response
            bytesAddressPair = self.UDPClientSocket.recvfrom(self.bufferSize)
            serverMessageArray = json.loads(bytesAddressPair[0])

            response = Response()

            return response.createResponseFromArray(serverMessageArray)
        except:
            return False
    
    def getResponses(self):
        while True:
            response = self.getResponse()
            
            # Append response to the shared queue
            if response:                   
                self.sharedQueue.put(response)

    def getQueue(self):
        return self.sharedQueue
        
    def createRoom(self):
        # Sending message to create room
        request = Request(requestCode=100)
        self.sendRequest(request)

        # Waiting for response
        return self.getResponse()

    def joinRoom(self, roomToken):
        self.currentRoom = roomToken

        # Sending message to join a room
        request = Request(requestCode=101, token=self.currentRoom)
        self.sendRequest(request=request)

        # Waiting for response
        return self.getResponse()
