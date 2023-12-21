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
        self.speed_x = 0
        self.pos_x, self.pos_y = pos_x, pos_y
        self.rect = self.image.get_rect().move(self.pos_x, self.pos_y)

    def update_jump(self):
        if pygame.sprite.spritecollideany(self, platform_group) and self.speed_y <= 0:
            self.speed_y = 4.5
        else:
            self.speed_y -= 0.1
        if self.speed_y >= 0:
            self.pos_y -= self.speed_y ** 2
        else:
            self.pos_y += self.speed_y ** 2
        self.rect.y = self.pos_y



if __name__ == '__main__':
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    running = True
    clock = pygame.time.Clock()
    Common_Plate(309, 700)
    Common_Plate(109, 700)
    Common_Plate(509, 700)
    player1 = Doodle(320, 630)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player1.rect.x -= 5
        elif keys[pygame.K_RIGHT]:
                player1.rect.x += 5
        if player1.rect.x + player1.rect.width // 2 < 0:
            player1.rect.x = width - player1.rect.width // 2
        elif player1.rect.x - player1.rect.width // 2 > width:
            player1.rect.x = - player1.rect.width // 2
        player1.update_jump()
        screen.blit(fon, (0, 0))
        platform_group.draw(screen)
        player.draw(screen)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
