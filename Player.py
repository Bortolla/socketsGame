# classe responsavel por manipular o jogador, como sua posicao, mapa, etc
class Player:
    def __init__(self, playerId=None, playerConnection=None, x=None, y=0, map=0, message=None, name=None) -> None:
        self.playerId = playerId                    # id unico do usuario 
        self.y = y                                  # posicao eixo Y
        self.x = x                                  # posicao eixo X
        self.map = map                              # mapa atual
        self.message = message                      # mensagem do jogador
        self.playerConnection = playerConnection    # conexao do jogador
        self.name = name                            # nome do jogador

    # retorna o nome do jogador
    def getPlayerName(self):
        return self.name

    # incrementa a posicao do jogador, e troca de mapa caso sua posicao seja
    # maior que o limite do mapa
    def incrementY(self):
        self.y = self.y + 100
        if self.y >= 650:
            self.y = 0
            self.map = self.map + 1
    
    # Muda o mapa do jogador
    def incrementMap(self):
        self.map = self.map + 1
    
    # Atribuir uma mensagem ao usuario
    def setMessage(self, message):
        self.message = message

    # retorna o ID do jogador
    def getPlayerId(self):
        return self.playerId
    
    # retorna eixo Y 
    def getY(self):
        return self.y
    
    # retorna eixo X 
    def getX(self):
        return self.x
    
    # retorna mensagem 
    def getMessage(self):
        return self.message

    # retorna mapa do jogador
    def getMap(self):
        return self.map
    
    # retorna conexao do jogador
    def getConnection(self):
        return self.playerConnection
    
    # reseta a posicao do jogador no mapa
    def resetY(self):
        self.y = 0

    # retorna as informacoes do jogador em forma de dicionario
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
    