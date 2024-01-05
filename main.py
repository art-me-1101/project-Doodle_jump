import pygame
import sys
import random
import os
import math

pygame.init()
size = width, height = 500, 1000
screen = pygame.display.set_mode(size)
FPS = 60
platform_group = pygame.sprite.Group()
start_pos = pygame.sprite.Group()
player = pygame.sprite.Group()
moving_platform_group = pygame.sprite.Group()
up_line = 500
break_platform_group = pygame.sprite.Group()
buttons_group = pygame.sprite.Group()
shuriken_group = pygame.sprite.Group()


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


def load_font(filename, size):
    fullname = os.path.join('font', filename)
    if not os.path.isfile(fullname):
        print(f"Файл со шрифтом '{fullname}' не найден")
        sys.exit()
    return pygame.font.Font(fullname, size)


class LavaSprite(pygame.sprite.Sprite):
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


lava = LavaSprite(load_image('Lava-Background-PNG-Image.png'), 4, 2, -100, 0)

platforms = {
    'common': load_image('common_plate.png'),
    'moving': load_image('moving plate.png'),
    'break': load_image('break_plate.png')
}
doodle = load_image('doodle.png')


class CommonPlate(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(platform_group)
        self.image = platforms['common']
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class BreakPlate(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(platform_group, break_platform_group)
        self.breaking = False
        self.time_since_last_animate = 0
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.speed_y = 0

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

    def break_plate(self, dt):
        if self.breaking:
            self.rect.y += self.speed_y ** 2
            self.speed_y += 0.2
            self.time_since_last_animate += dt
            if self.time_since_last_animate > 1:
                if self.cur_frame != len(self.frames) - 1:
                    self.time_since_last_animate = 0
                    self.update()


class MovingPlate(pygame.sprite.Sprite):
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
        self.a = 0

    def update_jump(self):
        sprite = pygame.sprite.spritecollideany(self, platform_group)
        if sprite is not None and self.speed_y <= 0:
            if sprite.rect.y > self.rect.y + self.rect.height // 3 * 2:
                if type(sprite) == BreakPlate:
                    sprite.breaking = True
                self.speed_y = 4.5
            else:
                self.speed_y -= 0.1
        else:
            self.speed_y -= 0.1
        if not (self.pos_y < up_line and self.speed_y > 0) and self.pos_y < height - self.rect.height:
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


class StartPoint(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(start_pos)
        image = load_image('start_point.png', -1)
        self.rect = image.get_rect().move(pos)


class Play(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(buttons_group)
        self.image = load_image('play.png')
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Shuriken(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, tg, pos, rot):
        super().__init__(shuriken_group)
        dur = math.atan(tg)
        self.rot = rot
        self.center = [*pos]
        self.speed = 20
        self.dx = math.cos(dur) * self.speed
        self.dy = math.sin(dur) * self.speed
        self.frames = []
        self.cur_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.y = self.center[1] - self.rect.h // 2
        self.rect.x = self.center[0] - self.rect.w // 2

    def update(self):
        self.center[0] -= self.dx * self.rot
        self.center[1] -= self.dy * self.rot
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect.y = self.center[1] - self.rect.h // 2
        self.rect.x = self.center[0] - self.rect.w // 2
        if 0 > self.rect.x + self.rect.w or width < self.rect.x - self.rect.w or \
                0 > self.rect.y + self.rect.h or height < self.rect.y - self.rect.h:
            self.kill()

    def cur_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


class Game:
    def __init__(self):
        lava.rect.y = height * 2
        self.score = 0
        self.fon = load_image('fon.png')
        self.top_score_line = load_image('top-score.png')
        self.clock = pygame.time.Clock()
        self.com_plate = 78
        self.break_plate = 21
        self.move_plate = 2
        self.defolt_space = 100
        self.space = self.defolt_space
        self.lava_speed = 4
        self.speed_doodle_x = 0
        CommonPlate(193, 700)
        for y in range(700 - self.space, 0, -self.space):
            CommonPlate(random.randrange(0, width - platforms['common'].get_width()), y)
        self.player1 = Doodle(215, 630)
        self.start_pos1 = StartPoint((self.player1.pos_x, self.player1.pos_y))
        self.camera = Camera((self.player1.rect.x, self.player1.rect.y))
        self.y_for_new_plate = self.player1.rect.y - up_line

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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = event.pos
                        x1, y1 = self.player1.rect.x + self.player1.rect.w // 2, \
                            self.player1.rect.y + self.player1.rect.h // 2
                        if x1 - x < 0:
                            a = -1
                        else:
                            a = 1
                        Shuriken(load_image('shuriken.png'), 3, 1, (y1 - y) / (x1 - x), (x1, y1), a)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if self.speed_doodle_x > -6:
                    self.speed_doodle_x -= 1
                self.player1.rect.x += self.speed_doodle_x
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if self.speed_doodle_x < 6:
                    self.speed_doodle_x += 1
                self.player1.rect.x += self.speed_doodle_x
            else:
                self.speed_doodle_x *= 0.9
                self.player1.rect.x += self.speed_doodle_x
            if self.player1.rect.x + self.player1.rect.width // 2 < 0:
                self.player1.rect.x = width - self.player1.rect.width // 2
            elif self.player1.rect.x - self.player1.rect.width // 2 > width:
                self.player1.rect.x = - self.player1.rect.width // 2
            self.player1.update_jump()
            for sprite in moving_platform_group:
                sprite.update()
            for sprite in break_platform_group:
                sprite.break_plate(dt)
            for sprite in shuriken_group:
                sprite.update()
            if (self.player1.speed_y > 0 and self.player1.pos_y < up_line) or \
                    self.player1.pos_y > height - self.player1.rect.height:
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
                        CommonPlate(random.randrange(0, width - platforms['common'].get_width()), 0)
                        self.space = self.defolt_space
                    elif n <= self.com_plate + self.move_plate:
                        MovingPlate(random.randrange(0, width - platforms['moving'].get_width()), 0)
                        self.space = self.defolt_space + 100
                    elif n <= self.com_plate + self.move_plate + self.break_plate:
                        BreakPlate(platforms['break'], 4, 1,
                                   random.randrange(0, width - platforms['moving'].get_width()), 0)
                        self.space = self.defolt_space
            if not platform_group and not g_o:
                lava.rect.y = height
                g_o = True
            if pygame.sprite.collide_mask(self.player1, lava):
                running = False
                self.game_over()
            screen.blit(self.fon, (-100, 0))
            platform_group.draw(screen)
            player.draw(screen)
            screen.blit(self.top_score_line, (0, -10))
            score_text = load_font('Comic Sans MS.ttf', 36).render(str(self.score // 10), True, (0, 0, 0))
            w_score_text = score_text.get_width()
            screen.blit(score_text, (width - w_score_text - 20, 0))
            screen.blit(lava.image, (lava.rect.x, lava.rect.y))
            buttons_group.draw(screen)
            shuriken_group.draw(screen)
            self.clock.tick(FPS)
            pygame.display.flip()
        pygame.quit()

    def game_over(self):
        for sprite in buttons_group:
            sprite.kill()
        running = True
        opacity = 0
        time_since_last_update = 0
        s = pygame.Surface((width, height))
        s.fill((0, 0, 0))
        s.set_alpha(opacity)
        font1 = load_font('Comic Sans MS.ttf', 86)
        game_over_text = font1.render('Game Over', False, (209, 13, 13))
        x_game_over_text = (width - game_over_text.get_width()) // 2
        font2 = load_font('Comic Sans MS.ttf', 45)
        score_text = font2.render(f'score: {self.score // 10}', True, (166, 166, 166))
        x_score_text = (width - score_text.get_width()) // 2
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if len(buttons_group) == 1:
                            if play.rect.collidepoint(*event.pos):
                                self.new_play()
                                self.__init__()
                                self.run()
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
            if opacity > 255:
                if not buttons_group:
                    play = Play(140, 800)
                screen.blit(game_over_text, (x_game_over_text, 200))
                screen.blit(score_text, (x_score_text, 200 + game_over_text.get_height()))
            buttons_group.draw(screen)
            self.clock.tick(FPS)
            pygame.display.flip()

    def new_play(self):
        for i in [platform_group, start_pos, player, moving_platform_group, break_platform_group, buttons_group,
                  shuriken_group]:
            for j in i:
                j.kill()


if __name__ == '__main__':
    game = Game()
    game.run()
