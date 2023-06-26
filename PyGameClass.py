import os                       # biblioteca do sistema operacional
import pygame                   # biblioteca pygame
from   pygame.locals import *   # biblioteca pygame
import pygame.freetype          # biblioteca pygame

# classe responsavel por fazer os desenhos na tela
class PyGameClass:
    def __init__(self) -> None:
        self.screenWidth = 850
        self.screenHeight = 660
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        self.playerWidth = 50
        self.playerHeight = 50
        self.clock = pygame.time.Clock()

        pygame.font.init()
        self.font = pygame.font.Font(None, 24)

    def drawMessages(self, messagesList):
        x = 100
        y = 50

        for i in range(0, len(messagesList)):
            text_surface = self.font.render(messagesList[i], True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y)
            self.screen.blit(text_surface, text_rect)

            y = y + 50

    def drawPlayer(self, playerObject):
        text_surface = self.font.render(playerObject.getPlayerName(), True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.center = (playerObject.getX() + 18, playerObject.getY() - 15)
        self.screen.blit(text_surface, text_rect)

        player_image = pygame.image.load('./images/spaceship.png')
        player_image = pygame.transform.scale(player_image, (self.playerWidth, self.playerHeight))
        player_rect = player_image.get_rect()
        player_rect.topleft = (playerObject.getX(), playerObject.getY())
        self.screen.blit(player_image, player_rect)

    def updateDisplay(self):
        pygame.display.update()
    
    def setTick(self, tick):
        self.clock.tick(tick)
    
    def fillScreen(self, fill):
        self.screen.fill(fill)
    
    def getEvents(self):
        return pygame.event.get()

    def playerPressedA(self):
        return pygame.key.get_pressed()[K_a]
    
    def setBackgroundImageForThisPlayer(self, thisPlayer):
        if thisPlayer.getMap() == 0:
            background_image = pygame.image.load('images/beach.png') 
        elif thisPlayer.getMap() == 1:
            background_image = pygame.image.load('images/grass.jpg')
        elif thisPlayer.getMap() == 2:
            background_image = pygame.image.load('images/ruins.png')
        elif thisPlayer.getMap() == 3:
            background_image = pygame.image.load('images/snow.jpg')
        elif thisPlayer.getMap() == 4:
            background_image = pygame.image.load('images/winter1.png')
        elif thisPlayer.getMap() == 5:
            background_image = pygame.image.load('images/winter2.png')

        background_image = pygame.transform.scale(background_image, (self.screenWidth, self.screenHeight))

        self.screen.blit(background_image, (0, 0))  
        pygame.display.flip()