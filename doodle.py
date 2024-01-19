import pygame
import math
from plate_and_difficult_object import BreakPlate, platform_group
from functions_and_constants import load_image, all_spite_group, width, up_line, height, load_sound

shuriken_group = pygame.sprite.Group()


class Doodle(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_spite_group)
        self.jump = load_sound('jump.mp3')
        self.breaking_platform = load_sound('breaking_platform.mp3')
        self.image = load_image('doodle.png')
        self.kill_d = False
        self.speed_y = 0
        self.speed_x = 0
        self.real_speed_y = 0
        self.pos_x, self.pos_y = pos_x, pos_y
        self.rect = self.image.get_rect().move(self.pos_x, self.pos_y)
        self.a = 0

    def update_jump(self):
        if self.rect.x + self.rect.width // 2 < 0:
            self.rect.x = width - self.rect.width // 2
        elif self.rect.x + self.rect.width // 2 > width:
            self.rect.x = - self.rect.width // 2
        sprite = pygame.sprite.spritecollideany(self, platform_group)
        if sprite is not None and self.speed_y <= 0:
            if sprite.rect.y > self.rect.y + self.rect.height - 28 and not self.kill_d:
                if type(sprite) == BreakPlate:
                    self.breaking_platform.play()
                    sprite.breaking = True
                self.jump.play()
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

    def kill_doodle(self):
        self.kill_d = True


class Camera:
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    def apply(self, obj, speed_y):
        obj.rect.y += speed_y


class Stars(pygame.sprite.Sprite):
    def __init__(self, player, sheet, columns, rows):
        super().__init__()
        self.player = player
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(player.rect.x + (player.rect.w - self.image.get_width()) // 2,
                                               player.rect.y)
        self.last_update = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, dt):
        self.last_update += dt
        self.rect.x = self.player.rect.x + (self.player.rect.w - self.image.get_width()) // 2 - 5
        self.rect.y = self.player.rect.y - 5
        if self.last_update > 20:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


class StartPoint(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.rect = pygame.Rect(1, 1, 1, 1).move(*pos)


class Shuriken(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, tg, pos, rot):
        super().__init__(shuriken_group, all_spite_group)
        dur = math.atan(tg)
        self.rot = rot
        self.center = [*pos]
        self.speed = 20
        if self.rot == -2:
            self.dy = self.speed * tg
            self.dx = 0
        else:
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
