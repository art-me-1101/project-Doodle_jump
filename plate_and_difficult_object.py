import pygame
from functions_and_constants import load_image, all_spite_group, width, height

fire_ball_group = pygame.sprite.Group()
monsters_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
moving_platform_group = pygame.sprite.Group()
break_platform_group = pygame.sprite.Group()


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


class FireBall(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, dur, y, player_pos):
        super().__init__(fire_ball_group, all_spite_group)
        if dur == -1:
            self.x = 0
        else:
            self.x = width
        self.y = y
        self.speed = 3
        px, py = player_pos
        dx, dy = self.x - px, self.y - py
        gip = (dx ** 2 + dy ** 2) ** 0.5
        self.dx = dx / gip * self.speed
        self.dy = dy / gip * self.speed
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.x, self.y)
        self.dt = 0
        self.rect.x -= self.rect.w // 2

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, dt):
        self.dt += dt
        if self.dt > 2:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.dt = 0
        self.rect.x -= self.dx
        self.rect.y -= self.dy
        if self.rect.x + self.rect.w + 50 < 0 or self.rect.x - 50 > width or self.rect.y - 50 > height or \
                self.rect.y + self.rect.w + 50 < 0:
            self.kill()


class MovingMonster(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(monsters_group, all_spite_group)
        self.x, self.y = x, y
        self.frames = []
        self.speed = 5
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.x, self.y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.rect.x + self.rect.w > width:
            self.speed = -5
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        elif self.rect.x < 0:
            self.speed = 5
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.rect.x += self.speed


class CommonPlate(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(platform_group, all_spite_group)
        self.image = load_image('common_plate.png')
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class BreakPlate(pygame.sprite.Sprite):
    def __init__(self, columns, rows, x, y):
        super().__init__(platform_group, break_platform_group, all_spite_group)
        self.breaking = False
        self.time_since_last_animate = 0
        self.frames = []
        self.cut_sheet(load_image('break_plate.png'), columns, rows)
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

    def update(self, dt):
        if self.breaking:
            self.rect.y += self.speed_y ** 2
            self.speed_y += 0.2
            self.time_since_last_animate += dt
            if self.time_since_last_animate > 1:
                if self.cur_frame != len(self.frames) - 1:
                    self.time_since_last_animate = 0
                    self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                    self.image = self.frames[self.cur_frame]


class MovingPlate(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(platform_group, moving_platform_group, all_spite_group)
        self.image = load_image('moving_plate.png')
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.direction = 3

    def update(self):
        if self.rect.x < 0:
            self.direction = 3
        elif self.rect.x + self.rect.width > width:
            self.direction = -3
        self.rect.x += self.direction
