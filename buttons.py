import pygame
from functions_and_constants import all_spite_group

buttons_group = pygame.sprite.Group()


class Button(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(buttons_group, all_spite_group)
        self.image = image
        self.rect = self.image.get_rect().move(pos_x, pos_y)
