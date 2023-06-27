import socket               # biblioteca de sockets
import threading            # biblioteca de threads
import secrets              # biblioteca para criacao de hashes
import json                 # biblioteca para manipulacao de JSON
from   Request  import *    # classe Request
from   Response import *    # classe Response
from   Player   import *    # classe Player

# Classe que trata de instanciar servidores TCP e UDP para comunicacao com o cliente,
# e fazer as manipulacoes necessarias, como tratar as requisicoes, criar salas, etc.
class ServerUDP:
    def __init__(self) -> None:
        self.udpAddressPort    = ('127.0.0.1', 20001) # (endereço, porta) servidor UDP
        self.tcpAddressPort = ('127.0.0.1', 20005)    # (endereço, porta) servidor TCP

        self.bufferSize      = 1024  # tamanho max em Bytes dos dados recebidos/enviados

        self.allRooms        = {}    # dicionaria de todas as salas

        # instancia do servidor UDP
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind(self.udpAddressPort)

        # instancia do servidor TCP
        self.TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCPServerSocket.bind(self.tcpAddressPort)
        self.TCPServerSocket.listen()

        self.TCPconnections = [] # conexoes TCP feitas ao servidor

        # dicionario com os enderecos TCP e UDP respectivos ao mesmo cliente
        self.TCPTOUDP       = {}  # (endereço, porta) TCP: (endereço, porta) UDP
        
    # retorna o correspondente endereco UDP com base no endereco TCP de um cliente
    def fromTcpToUdp(self, tcpaddress):
        if tcpaddress in self.TCPTOUDP:
            return self.TCPTOUDP[tcpaddress] # endereco UDP do cliente
        return None
        
    # Recebe requisição UDP contendo os dados da requisição e o endereço do cliente
    # retorna uma instancia da classe Request a partir dos dados enviados pelo cliente
    def getUDPRequest(self):
        try:
            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            clientMessageArray = json.loads(bytesAddressPair[0]) # dados enviados na requisicao
            clientMessageArray['address'] =  bytesAddressPair[1] # endereco do cliente
            request = Request()
            
            return request.createRequestFromArray(clientMessageArray)
        
        except:
            return False
    
    # Recebe requisicao TCP e retorna uma instancia da classe Requisicao
    # a partir dos dados enviados 
    def getTCPRequest(self):
        # objeto conexao TCP, e (endereco, porta)
        conn, addr = self.TCPServerSocket.accept()

        # recebe o dado em formato JSON e converte para dicionario Python
        clientMessageArray = json.loads(conn.recv(self.bufferSize))
        clientMessageArray['address'] =  addr   # endereco do cliente
        clientMessageArray['connection'] = conn # objeto socket 

        request = Request()

        return request.createRequestFromArray(clientMessageArray)
       
    # envia uma resposta UDP
    def sendReponseWithUDP(self, response, address):
        # cria um JSON com base na Resposta, e entao transforma em uma string
        bytesToSend = str.encode(json.dumps(response.getResponseAsArray()))
        self.UDPServerSocket.sendto(bytesToSend, address) # envia para o endereco

    # envia uma resposta TCP
    def sendReponseWithTCP(self, response, connection):
        # cria um JSON com base na Resposta, e entao transforma em uma string
        bytesToSend = str.encode(json.dumps(response.getResponseAsArray()))
        connection.sendall(bytesToSend) # envia para o endereco

    # Pega os dados da conexao de um cliente TCP
    def getConnectionData(self, request):   
        # Dados enviados como JSON sao convertidos para dicionario
        try:
            clientMessageArray = json.loads(request.getConnection().recv(self.bufferSize))

        except:
            return False

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
        
        # retorna o token identificador da sala criada
        return token
    
    # adiciona um usuario a uma sala ja existente
    def addUserToRoom(self, token, userAddress, playerConnection, playerName):
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
            users[userAddress] = Player(playerId=userAddress, playerConnection=playerConnection, x=x, name=playerName)

            # retorna o dicionario de usuarios atualizado
            return users

    # retorna todas as conexoes TCP
    def getTCPConnections(self):
        return self.TCPconnections
    
    # retorna todas as salas
    def getAllRooms(self):
        return self.allRooms
    
    # retorna todos os jogadores de uma sala
    def getRoomUsers(self, token):
        if token in self.allRooms:                  # se a sala existir
            return self.allRooms[token]['users']    # enviar seus usuarios
        
        return False
    
    # retorna o(s) vencedor(es) de uma sala
    def getRoomWinners(self, token):
        if token in self.allRooms:                  # se a sala existir
            return self.allRooms[token]['winners']  # envia seus vencedores
        
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

        # manipula todas as requisicoes que forem recebidas
        while True:
            if not firstRequest == True:
                request = self.getConnectionData(request=request)
                if request == False:
                    break

            if request:
                firstRequest = False
                
                # requisicao codigo 100 cria uma nova sala
                if request.getRequestCode() == 100:
                    newRoomToken = self.createNewRoom()

                    # envia resposta de sucesso com o token da sala
                    response = Response(responseCode=201, token=newRoomToken)
                    self.sendReponseWithTCP(response, request.getConnection())

                # requisicao codigo 103 lista todas as salas
                elif request.getRequestCode() == 103:
                    returnData = []

                    # adiciona todas as salas no dado de retorno
                    for room in self.getAllRooms():
                        returnData.append(room)
                    
                    # envia resposta de sucesso com todas as salas
                    response = Response(responseCode=200, returnData=returnData)
                    self.sendReponseWithTCP(response, request.getConnection())

                # requisicao codigo 101 usuario entra em uma sala
                elif request.getRequestCode() == 101:
                    token = request.getToken() # pega o token enviado na requisicao
                    
                    # [endereco, porta UDP]
                    clientUdpAddr = (request.getRequestData()['UDPAddress'][0], request.getRequestData()['UDPAddress'][1])
                    
                    # adiciona um usuario na sala especificada, utilizando seu 
                    # endereço, conexao e nome passado
                    usersInRoom = self.addUserToRoom(token=token, userAddress=request.getAddress(), playerConnection=request.getConnection(), playerName=request.getRequestData()['name'])

                    # caso retorne False entao enviar mensagem de erro
                    if not usersInRoom:
                        response = Response(responseCode=400)
                        self.sendReponseWithTCP(response, request.getConnection())
                    else: 
                        # caso contrario, adicionar sua conexao UDP atrelada a sua
                        # conexao TCP: (endereço, porta) TCP : (endereço, porta) UDP
                        self.TCPTOUDP[request.getAddress()] = clientUdpAddr

                        # mensagem para o cliente
                        returnData = {}
                        returnData['message'] = '{} entrou na sala. {}/3'.format(request.getRequestData()['name'], len(usersInRoom))
                        
                        # informacoes do jogador (posicao, velocidade, ...)
                        returnData['playerInfo'] = usersInRoom[request.getAddress()].getPlayerAsArray()
                        
                        # informacoes de cima enviadas para cada um dos usuarios na sala
                        for address in usersInRoom:
                            response = Response(responseCode=202, returnData=returnData)
                            self.sendReponseWithTCP(response, usersInRoom[address].getConnection())

                        # caso a sala ja esteja cheia
                        if len(usersInRoom) >= 3:
                            # mensagem de retorno para os usuarios
                            returnData = {}
                            returnData['message'] = 'Partida pronta. {}/3'.format(len(usersInRoom))

                            # array de jogadores no campo players do dicionario
                            returnData['players'] = [] 

                            # para cada jogador na sala, sao armazenadas suas 
                            # informacoes de partida (posicao, ...)
                            for address in usersInRoom:
                                returnData['players'].append(usersInRoom[address].getPlayerAsArray())

                            # os dados sao repassados para cada um dos jogadores
                            # na sala
                            for address in usersInRoom:
                                response = Response(responseCode=203, returnData=returnData)
                                self.sendReponseWithTCP(response, usersInRoom[address].getConnection())

    # metodo que manipula as conexoes UDP
    def handleUDPRequest(self, request):
        requestData = request.getRequestData() # dados da requisicao

        requestData['tcpAddress'] = (requestData['tcpAddress'][0], requestData['tcpAddress'][1]) # (endereço, porta) UDP do cliente

        # Requisicao com codigo 102 eh quando o usuario ja esta em uma sala
        # e deseja atualizar as informacoes da partida (posicao, ...)
        if request.getRequestCode() == 102:
            token = request.getToken()                      # token da sala
            usersInRoom = self.getRoomUsers(token=token)    # jogadores da sala
            roomWinners = self.getRoomWinners(token=token)  # vencedores da partida

            # se getRoomUsers retorna um erro, enviar msg de erro para cliente
            if not usersInRoom:
                print('1')
                response = Response(responseCode=400)
                self.sendReponseWithUDP(response, self.fromTcpToUdp(requestData['tcpAddress']))
            
            # se o usuario nao estiver na sala, enviar mensagem de erro
            elif not (requestData['tcpAddress'] in usersInRoom):
                print(requestData['tcpAddress'])
                print('2')
                response = Response(responseCode=400)
                self.sendReponseWithUDP(response, self.fromTcpToUdp(requestData['tcpAddress']))

            # se o cliente estiver entre os vencedores,
            # enviar mensagem de vitoria e sua posicao ao finalizar a corrida
            elif requestData['tcpAddress'] in roomWinners:
                returnData = 'Voce ficou em {} lugar'.format(roomWinners.index(requestData['tcpAddress']) + 1)
                
                response = Response(responseCode=207, returnData=returnData)
                self.sendReponseWithUDP(response, self.fromTcpToUdp(requestData['tcpAddress']))

            # se o usuario apertou a tecla 'a', significa que ele deu um passo
            # para frente
            elif requestData['pressedKey'] == 'a':
                # para cada jogador na sala, procurar qual jogador se movimentou
                # com base no seu id e o endereco tcp enviado, e quando for encontrado
                for player in usersInRoom:
                    if usersInRoom[player].getPlayerId() == requestData['tcpAddress']:
                        playerObject = usersInRoom[player] # armazenar sua instancia
                        break

                playerObject.incrementY() # e incrementar sua posicao em 1 valor

                # se o usuario terminou o mapa 6, entao ele chegou ao fim,
                # entao adiciona-lo aos vencedores, e enviar mensagem de vitoria
                if playerObject.getMap() >= 6:
                    roomWinners.append(requestData['tcpAddress'])
                    returnData = '{} ficou em {} lugar'.format(requestData['name'], roomWinners.index(requestData['tcpAddress']) + 1)
                    response = Response(responseCode=206, returnData=returnData)
                else: # senao, enviar resposta com a posicao atualziada
                    returnData = playerObject.getPlayerAsArray()
                    response = Response(responseCode=205, returnData=returnData)

                # Enviando a resposta com as informacoes atualizadas para todos
                # os clientes na sala
                for user in usersInRoom:
                    self.sendReponseWithUDP(response, self.fromTcpToUdp(user))
                
                # se a sala ja tem 3 vencedores (mesmo numero max/min de jogadores),
                # entao todos chegaram ao fim, logo, a partida acabou
                if len(roomWinners) >= 3:
                    self.allRooms.pop(token) # retirar o token das salas listadas
                    for user in usersInRoom: # enviar resposta para todos
                        returnData = 'A partida acabou'
                        response = Response(responseCode=210, returnData=returnData)
                        self.sendReponseWithUDP(response, self.fromTcpToUdp(user))
            
            # enviar mensagem de erro
            else:
                print('3')
                response = Response(responseCode=400)
                self.sendReponseWithUDP(response, self.fromTcpToUdp(user))
        
        # enviar mensagem para os usuarios da sala
        if request.getRequestCode() == 199:
            requestData = request.getRequestAsArray()
            messageData = requestData['requestData']

            #print(f"{messageData['name']}: {messageData['message']}")

            #print(f'requestData:\n{requestData}')
            #print(f'\nmessageData:\n{messageData}')
            
            roomToken = requestData['token']
            usersInRoom = self.getRoomUsers(roomToken)

            returnData = f"{messageData['name']}: {messageData['message']}"

            for user in usersInRoom:
                response = Response(responseCode=299, returnData=returnData)

                self.sendReponseWithUDP(response, self.fromTcpToUdp(user))