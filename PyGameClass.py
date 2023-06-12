import pygame
from   pygame.locals import *

class PyGameClass:
    def __init__(self) -> None:
        self.screenWidth = 850
        self.screenHeight = 660
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        self.playerWidth = 50
        self.playerHeight = 50
        self.clock = pygame.time.Clock()

    def drawPlayer(self, playerObject):
        pygame.draw.rect(
            self.screen, 
            (255, 0, 0),  
            (playerObject.getX(), playerObject.getY(), self.playerWidth, self.playerHeight)
        )

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
