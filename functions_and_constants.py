import os
import pygame
import sys

size = width, height = 500, 1000
up_line = 500
FPS = 60
all_spite_group = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

def load_sound(name):
    fullname = os.path.join('sound', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    return pygame.mixer.Sound(fullname)

def load_font(filename, size):
    fullname = os.path.join('font', filename)
    if not os.path.isfile(fullname):
        print(f"Файл со шрифтом '{fullname}' не найден")
        sys.exit()
    return pygame.font.Font(fullname, size)