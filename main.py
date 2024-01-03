import pygame
import sys
import random
import os

pygame.init()
size = width, height = 500, 1000
screen = pygame.display.set_mode(size)
FPS = 60
platform_group = pygame.sprite.Group()
start_pos = pygame.sprite.Group()
player = pygame.sprite.Group()
moving_platform_group = pygame.sprite.Group()
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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


lava = AnimatedSprite(load_image('Lava-Background-PNG-Image.png'), 4, 2, -100, 2 * height + 500)

platforms = {
    'common': load_image('common_plate.png'),
    'moving': load_image('moving plate.png')
}
doodle = load_image('doodle.png')


class Common_Plate(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(platform_group)
        self.image = platforms['common']
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Moving_Plate(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(platform_group, moving_platform_group)
        self.image = platforms['moving']
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.direction = 3

    def update(self):
        if self.rect.x < 0:
            self.direction = 3
        elif self.rect.x + self.rect.width > width:
            self.direction = -3
        self.rect.x += self.direction


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
        if not (self.pos_y < up_line and self.speed_y > 0) and self.pos_y < 950 - self.rect.height:
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
        self.clock = pygame.time.Clock()
        self.com_plate = 98
        self.move_plate = 3
        self.space = 100
        Common_Plate(193, 700)
        for y in range(700 - self.space, 0, -self.space):
            n = random.randrange(0, 101)
            if n <= self.com_plate:
                Common_Plate(random.randrange(0, width - platforms['common'].get_width()), y)
            elif n <= self.com_plate + self.move_plate:
                Moving_Plate(random.randrange(0, width - platforms['moving'].get_width()), y)
        self.player1 = Doodle(215, 630)
        self.start_pos1 = Start_point((self.player1.pos_x, self.player1.pos_y))
        self.camera = Camera((self.player1.rect.x, self.player1.rect.y))
        self.y_for_new_plate = self.player1.rect.y - up_line
        self.lava_speed = 4

    def run(self):
        time_since_last_update = 0
        running = True
        g_o = False
        while running:
            lava.rect.y = lava.rect.y - self.lava_speed
            dt = self.clock.tick()
            time_since_last_update += dt
            if time_since_last_update > 10:
                lava.update()
                time_since_last_update = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
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
            for sprite in moving_platform_group:
                sprite.update()
            if (self.player1.speed_y > 0 and self.player1.pos_y < up_line) or \
                    self.player1.pos_y > 950 - self.player1.rect.height:
                for sprite in platform_group:
                    self.camera.apply(sprite, self.player1.real_speed_y)
                    if sprite.rect.y > height + 50 or sprite.rect.y < -200:
                        sprite.kill()
                self.camera.apply(self.start_pos1, self.player1.real_speed_y)
                if lava.rect.y < height * 2:
                    self.camera.apply(lava, self.player1.real_speed_y)
            if self.score < self.start_pos1.rect.y - self.player1.rect.y:
                self.score = self.start_pos1.rect.y - self.player1.rect.y
                if self.y_for_new_plate < self.score - self.space:
                    self.y_for_new_plate += self.space
                    n = random.randrange(0, 101)
                    if n <= self.com_plate:
                        Common_Plate(random.randrange(0, width - platforms['common'].get_width()), 0)
                        self.space = 100
                    elif n <= self.com_plate + self.move_plate:
                        Moving_Plate(random.randrange(0, width - platforms['moving'].get_width()), 0)
                        self.space = 200
            if not platform_group and not g_o:
                lava.rect.y = height
                g_o = True
            if pygame.sprite.collide_mask(self.player1, lava):
                running = False
                self.game_over()
            screen.blit(self.fon, (0, 0))
            platform_group.draw(screen)
            player.draw(screen)
            screen.blit(lava.image, (lava.rect.x, lava.rect.y))
            self.clock.tick(FPS)
            pygame.display.flip()
        pygame.quit()

    def game_over(self):
        running = True
        opacity = 0
        time_since_last_update = 0
        s = pygame.Surface((width, height))
        s.fill((0, 0, 0))
        s.set_alpha(opacity)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if lava.rect.y > 0:
                lava.rect.y -= 10
            dt = self.clock.tick()
            time_since_last_update += dt
            if time_since_last_update > 10:
                lava.update()
                time_since_last_update = 0
            screen.blit(self.fon, (0, 0))
            platform_group.draw(screen)
            player.draw(screen)
            screen.blit(lava.image, (lava.rect.x, lava.rect.y))
            if lava.rect.y <= 0:
                if opacity < 255:
                    opacity += 10
                s.set_alpha(opacity)
            screen.blit(s, (0, 0))
            self.clock.tick(FPS)
            pygame.display.flip()


if __name__ == '__main__':
    game = Game()
    game.run()
