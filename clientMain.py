from   ClientUDP     import *
from   Player        import *
from   pygame.locals import *
from   PyGameClass   import *
from   sys           import exit
import pygame
import threading

ClientUDPClass = ClientUDP()

stop = False
while stop != True:
    print('MENU: 1. Criar sala 2. Listar salas 3. Entrar em uma sala')
    action = str(input('-> ')).strip()

    if not action in ['1', '2', '3', '1.', '2.', '3.']:
        print('Comando invalido')
    elif action in ['1', '1.']:
        response = ClientUDPClass.createRoom()

        if not response or response.getResponseCode() != 201:
            print('Erro ao criar sala. Tente novamente')
        elif response.getResponseCode() == 201:
            print('Sala criada. Chave de acesso: {}'.format(response.getToken()))
        

    elif action in ['2', '2.']:
        response = ClientUDPClass.listRooms()

        if not response or response.getResponseCode() != 200:
            print('Erro ao listar salas. Tente novamente')
        elif response.getResponseCode() == 200:
            roomsList = response.getReturnData()

            if len(roomsList) < 1:
                print('Nao ha salas disponiveis')
            else:
                for i in range(0, len(roomsList)):
                    print('Sala {}: {}'.format(i + 1, roomsList[i]))

    elif action in ['3', '3.']:
        roomToken = str(input('Informe o token da sala: ')).strip()
        response = ClientUDPClass.joinRoom(roomToken=roomToken)

        if not response:
            print('Erro inesperado. Tente novamente')
        elif response.getResponseCode() != 202:
            print('Chave de acesso invalida ou sala cheia. Tente novamente.')
        elif response.getResponseCode() == 202:
            playerInfoArray = response.getReturnData()['playerInfo']
            thisPlayer = Player(playerId=playerInfoArray['playerId'], x=playerInfoArray['x'])

            print('Voce entrou na sala. Aguardando usuarios.')
            while True:
                response = ClientUDPClass.getTCPResponse()

                if not response:
                    pass

                # Waiting for users to join
                elif response.getResponseCode() == 202:
                    print(response.getReturnData()['message'])

                # Match is ready
                elif response.getResponseCode() == 203:
                    responseData = response.getReturnData()
                    print(responseData['message'])

                    # List to append the other players objects
                    playerObjects = []
                    for player in responseData['players']:
                        if player['playerId'] != thisPlayer.getPlayerId():
                            playerObject = Player(playerId=player['playerId'], x=player['x'])
                            playerObjects.append(playerObject)
                    
                    # Putting the other players on variables
                    player1 = playerObjects[0]
                    player2 = playerObjects[1]

                    # Object for handling pyGame
                    pyGameObject = PyGameClass()

                    # Drawing the right image for this player location
                    pyGameObject.setBackgroundImageForThisPlayer(thisPlayer)
                    
                    # Drawing players in their first positions
                    pyGameObject.drawPlayer(thisPlayer)
                    pyGameObject.drawPlayer(player1)
                    pyGameObject.drawPlayer(player2)
                    
                    # Update the drawings to the display
                    pyGameObject.updateDisplay()
                    
                    # Starts thread to get responses
                    getResponsesThread = threading.Thread(target=ClientUDPClass.getResponses)
                    getResponsesThread.start()

                    while True:
                        pyGameObject.setTick(30)
                        pyGameObject.fillScreen((0,0,0))

                        # Getting the action of the player and sending to the server
                        requestData = {}
                        for event in pyGameObject.getEvents():
                            if event.type == QUIT:
                                pygame.quit()
                                exit()

                            #elif event.type == KEYDOWN and event.key == K_a:
                            elif pyGameObject.playerPressedA():
                                requestData['pressedKey'] = 'a'
                                request = Request(
                                    requestCode=102, 
                                    token=ClientUDPClass.currentRoom, 
                                    requestData=requestData
                                )
                                ClientUDPClass.sendRequestWithUDP(request=request)

                        # Checking for data from the server
                        if not ClientUDPClass.getQueue().empty():
                            # Getting the next response from server
                            response = ClientUDPClass.getQueue().get()
                            
                            # Code 206: player just got to the finish line
                            if response.getResponseCode() == 206:
                                print(response.getReturnData())
                            # Code 207: player already got to the finish line
                            elif response.getResponseCode() == 207:
                                print(response.getReturnData())
                            # Code 210: match finished
                            elif response.getResponseCode() == 210:
                                print(response.getReturnData())
                            # Code 205: player is in match
                            elif response.getResponseCode() == 205:
                                # The responseData here is the new position of one of the players
                                responseData = response.getReturnData()
                                # Creating a player object with de new data
                                playerNewInfo = Player(playerId=responseData['playerId'], x=responseData['x'], y=responseData['y'], map=responseData['map'], message=responseData['message'])

                                # Setting the new data to the right player
                                if thisPlayer.getPlayerId() == playerNewInfo.getPlayerId():
                                    thisPlayer = playerNewInfo
                                elif player1.getPlayerId() == playerNewInfo.getPlayerId():
                                    player1 = playerNewInfo
                                elif player2.getPlayerId() == playerNewInfo.getPlayerId():
                                    player2 = playerNewInfo

                                # Drawing the right image for this player location
                                pyGameObject.setBackgroundImageForThisPlayer(thisPlayer)
                                
                                # Drawing the players on the same map of this player
                                if thisPlayer.getMap() == player1.getMap() and thisPlayer.getMap() == player2.getMap():
                                    pyGameObject.drawPlayer(thisPlayer)
                                    pyGameObject.drawPlayer(player1)
                                    pyGameObject.drawPlayer(player2)

                                elif thisPlayer.getMap() == player1.getMap():
                                    pyGameObject.drawPlayer(thisPlayer)
                                    pyGameObject.drawPlayer(player1)

                                elif thisPlayer.getMap() == player2.getMap():
                                    pyGameObject.drawPlayer(thisPlayer)
                                    pyGameObject.drawPlayer(player2)

                                else:
                                    pyGameObject.drawPlayer(thisPlayer)

                                # Update the drawings to the display
                                pyGameObject.updateDisplay()

                            else:
                                print('Algo deu errado')
