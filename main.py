import pygame
import sys
import os

pygame.init()
size = width, height = 700, 1000
screen = pygame.display.set_mode(size)
fps = 60
platform_group = pygame.sprite.Group()
player = pygame.sprite.Group()


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


platforms = {
    'common': load_image('common_plate.png')
}
doodle = load_image('doodle.png')


class Common_Plate(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(platform_group)
        self.image = platforms['common']
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Doodle(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player)
        self.image = doodle
        self.speed_y = 0
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update_jump(self):
        pass


if __name__ == '__main__':
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    running = True
    clock = pygame.time.Clock()
    Common_Plate(309, 700)
    Doodle(320, 630)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.blit(fon, (0, 0))
        platform_group.draw(screen)
        player.draw(screen)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
