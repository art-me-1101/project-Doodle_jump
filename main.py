import pygame
import sys
import random
import os

pygame.init()
size = width, height = 500, 1000
screen = pygame.display.set_mode(size)
fps = 60
platform_group = pygame.sprite.Group()
start_pos = pygame.sprite.Group()
player = pygame.sprite.Group()
space = 100
up_line = 500


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
        self.real_speed_y = 0
        self.pos_x, self.pos_y = pos_x, pos_y
        self.rect = self.image.get_rect().move(self.pos_x, self.pos_y)

    def update_jump(self):
        sprite = pygame.sprite.spritecollideany(self, platform_group)
        if sprite is not None and self.speed_y <= 0:
            if sprite.rect.y > self.rect.y + self.rect.height // 2:
                self.speed_y = 4.5
            else:
                self.speed_y -= 0.1
        else:
            self.speed_y -= 0.1
        if not (self.pos_y < up_line and self.speed_y > 0):
            if self.speed_y >= 0:
                self.pos_y -= self.speed_y ** 2
                self.real_speed_y = self.speed_y ** 2
            else:
                self.pos_y += self.speed_y ** 2
                self.real_speed_y = -self.speed_y ** 2
        else:
            if self.speed_y >= 0:
                self.real_speed_y = self.speed_y ** 2
            else:
                self.real_speed_y = -self.speed_y ** 2
        self.rect.y = self.pos_y


class Camera:
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    def apply(self, obj, speed_y):
        obj.rect.y += speed_y


class Start_point(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(start_pos)
        image = load_image('start_point.png', -1)
        self.rect = image.get_rect().move(pos)


class Game:
    def __init__(self):
        self.score = 0
        self.fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
        self.running = True
        self.clock = pygame.time.Clock()
        Common_Plate(309, 700)
        for y in range(700 - space, 0, -space):
            Common_Plate(random.randrange(0, width - platforms['common'].get_width()), y)
        self.player1 = Doodle(320, 630)
        self.start_pos1 = Start_point((self.player1.pos_x, self.player1.pos_y))
        self.camera = Camera((self.player1.rect.x, self.player1.rect.y))
        self.y_for_new_plate = self.player1.rect.y - up_line

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player1.rect.x -= 5
            elif keys[pygame.K_RIGHT]:
                self.player1.rect.x += 5
            if self.player1.rect.x + self.player1.rect.width // 2 < 0:
                self.player1.rect.x = width - self.player1.rect.width // 2
            elif self.player1.rect.x - self.player1.rect.width // 2 > width:
                self.player1.rect.x = - self.player1.rect.width // 2
            self.player1.update_jump()
            if (self.player1.speed_y > 0 and self.player1.pos_y < up_line) or self.player1.pos_y > 900:
                for sprite in platform_group:
                    self.camera.apply(sprite, self.player1.real_speed_y)
                    if sprite.rect.y > height + 50 or sprite.rect.y < -200:
                        sprite.kill()
                self.camera.apply(self.start_pos1, self.player1.real_speed_y)
            if self.score < self.start_pos1.rect.y - self.player1.rect.y:
                self.score = self.start_pos1.rect.y - self.player1.rect.y
                if self.y_for_new_plate < self.score - space:
                    self.y_for_new_plate += space
                    Common_Plate(random.randrange(0, width - platforms['common'].get_width()), 0)
            if not platform_group.sprites():
                self.game_over()
            screen.blit(self.fon, (0, 0))
            platform_group.draw(screen)
            player.draw(screen)
            self.clock.tick(fps)
            pygame.display.flip()
        pygame.quit()

    def game_over(self):
        while self.player1.rect.y < height:
            self.player1.update_jump()
        print('game_over')
        self.running = False


if __name__ == '__main__':
    game = Game()
    game.run()
