import pygame
import os
import random

ASTEROID = pygame.image.load(os.path.join("assets", "asteroid.png"))


class Asteroid:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.asteroid_img = ASTEROID
        self.mask = pygame.mask.from_surface(self.asteroid_img)

    def draw(self, window):
        window.blit(self.asteroid_img, (self.x, self.y))

    def get_width(self):
        return self.asteroid_img.get_width()

    def get_height(self):
        return self.asteroid_img.get_height()