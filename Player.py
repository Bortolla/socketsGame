class Player:
    def __init__(self, playerId=None, playerConnection=None, x=None, y=0, map=0, message=None, name=None) -> None:
        self.playerId = playerId
        self.y = y
        self.x = x
        self.map = map
        self.message = message
        self.playerConnection = playerConnection
        self.name = name

    def getPlayerName(self):
        return self.name

    def incrementY(self):
        self.y = self.y + 100
        if self.y >= 650:
            self.y = 0
            self.map = self.map + 1
    
    def incrementMap(self):
        self.map = self.map + 1
    
    def setMessage(self, message):
        self.message = message

    def getPlayerId(self):
        return self.playerId
    
    def getY(self):
        return self.y
    
    def getX(self):
        return self.x
    
    def getMessage(self):
        return self.message

    def getMap(self):
        return self.map
    
    def getConnection(self):
        return self.playerConnection
    
    def resetY(self):
        self.y = 0

    def getPlayerAsArray(self):
        returnData = {
            'playerId': self.playerId,
            'y': self.y,
            'x': self.x,
            'map': self.map,
            'message': self.message,
            'name': self.name
        }

        return returnData
    