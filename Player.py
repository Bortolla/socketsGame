class Player:
    def __init__(self, playerId=None, x=None, y=0, map=0, message=None) -> None:
        self.playerId = playerId # ID do jogador 
        self.y = y # posicao no eixo Y no mapa 
        self.x = x # posicao no eixo Y no mapa 
        self.map = map # mapa atual sendo jogado
        self.message = message # mensagem do jogo

    # incrementa posicao no eixo Y em 10
    def incrementY(self):
        self.y = self.y + 10
        # caso a posicao do jogador exceda o numero 10, o mapa eh trocado e sua posicao reseta
        if self.y >= 650:
            self.y = 0
            self.map = self.map + 1
    
    # troca de mapa
    def incrementMap(self):
        self.map = self.map + 1
    
    # apresenta mensagem para os jogadores da partida
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
    
    def resetY(self):
        self.y = 0

    # informacoes do jogador em forma de um dicionario
    def getPlayerAsArray(self):
        returnData = {
            'playerId': self.playerId,
            'y': self.y,
            'x': self.x,
            'map': self.map,
            'message': self.message
        }

        return returnData
    