import pygame
import random
import sqlite3
from plate_and_difficult_object import BreakPlate, MovingPlate, CommonPlate, MovingMonster, FireBall, monsters_group, \
    platform_group, break_platform_group, moving_platform_group, fire_ball_group, LavaSprite
from doodle import Doodle, Stars, Shuriken, shuriken_group, StartPoint, Camera
from buttons import buttons_group, Button
from functions_and_constants import load_image, load_font, size, all_spite_group, width, height, up_line, FPS, \
    load_sound

pygame.init()
screen = pygame.display.set_mode(size)


class Game:
    def __init__(self, difficult):
        try:
            open('last_name.txt')
        except FileNotFoundError:
            with open('last_name.txt', 'w', encoding='utf-8') as f:
                f.write('')
        con = sqlite3.connect('lider_table.sgl')
        cur = con.cursor()
        cur.execute('''
                CREATE TABLE IF NOT EXISTS Scores (
                name TEXT NOT NULL,
                score INTEGER NOT NULL
                )
                ''')
        con.commit()
        con.close()
        self.dif = difficult
        self.pause_fon = load_image('pause-cover.png')
        self.pause = Button(10, 10, load_image('pause.png'))
        self.pause_game = False
        self.lava = LavaSprite(load_image('Lava-Background-PNG-Image.png'), 4, 2, -100, height * 2)
        self.score = 0
        self.fon = load_image('fon.png')
        self.top_score_line = load_image('top-score.png')
        self.clock = pygame.time.Clock()
        self.extra_score = 0
        if self.dif == 1:
            self.com_plate = 76
            self.break_plate = 20
            self.move_plate = 2
            self.mov_monst = 1
            self.lava_speed = 2
            self.fire_chace = 1
            self.score_mult = 1 / 6
        elif self.dif == 2:
            self.com_plate = 50
            self.break_plate = 35
            self.move_plate = 10
            self.mov_monst = 5
            self.lava_speed = 3
            self.fire_chace = 5
            self.score_mult = 1 / 4
        elif self.dif == 3:
            self.com_plate = 45
            self.break_plate = 30
            self.move_plate = 15
            self.mov_monst = 10
            self.lava_speed = 4
            self.fire_chace = 8
            self.score_mult = 1 / 2
        self.score_to_new_update = 500
        self.fire_count = 3
        self.score_for_update = self.score_to_new_update
        self.defolt_space = 100
        self.space = self.defolt_space
        self.heals = 3
        self.kill = False
        self.speed_doodle_x = 0
        self.player = Doodle(215, 630)
        self.start_pos = StartPoint((self.player.pos_x, self.player.pos_y))
        self.camera = Camera((self.player.rect.x, self.player.rect.y - 5))
        self.y_for_new_plate = self.player.rect.y - up_line
        self.stars = Stars(self.player, load_image('stars.png'), 4, 1)

    def run_win(self):
        self.del_groups()
        a = self.run()
        while a is not None:
            if type(a) == StartWindow:
                return StartWindow
            a = a()
        return None

    def run(self):
        pygame.mixer.stop()
        game_music = load_sound('game_music.mp3')
        game_music.set_volume(0.2)
        game_music.play(loops=-1)
        last_obj_is_monst = False
        fire_balls = {
            'l': [load_image('fire_ball_orange_L.png'), load_image('fire_ball_purple_L.png'),
                  load_image('fire_ball_blue_L.png')],
            'r': [load_image('fire_ball_orange_R.png'), load_image('fire_ball_purple_R.png'),
                  load_image('fire_ball_blue_R.png')]
        }
        heard = load_image('heals.png')
        font1 = load_font('Comic Sans MS.ttf', 70)
        doodle_jump_text = font1.render('Doodle jump', True, (255, 0, 0))
        doodle_jump_text = pygame.transform.rotate(doodle_jump_text, 20)
        d_j_t_x = (width - doodle_jump_text.get_width()) // 2
        font2 = load_font('Comic Sans MS.ttf', 50)
        pause_text = font2.render('pause', True, (125, 125, 125))
        pause_text = pygame.transform.rotate(pause_text, 20)
        pause_x = (width - pause_text.get_width()) // 2 - 20
        CommonPlate(193, 700)
        for y in range(700 - self.space, 0, -self.space):
            CommonPlate(random.randrange(0, width - load_image('common_plate.png').get_width()), y)
        time_since_last_update = 0
        running = True
        g_o = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.pause.rect.collidepoint(*event.pos):
                            self.pause_game = True
                            resume = Button(138, height - 200, load_image('resume.png'))
                            menu = Button(138, height - 100, load_image('menu.png'))
                        elif self.pause_game:
                            if resume.rect.collidepoint(*event.pos):
                                self.pause_game = False
                                resume.kill()
                                menu.kill()
                            if menu.rect.collidepoint(*event.pos):
                                return StartWindow
                        elif len(shuriken_group) < 2:
                            x, y = event.pos
                            x1, y1 = self.player.rect.x + self.player.rect.w // 2, \
                                self.player.rect.y + self.player.rect.h // 2
                            if x1 - x < 0:
                                a = -1
                            else:
                                a = 1
                            if x1 - x == 0:
                                if (y1 - y) > 0:
                                    Shuriken(load_image('shuriken.png'), 3, 1, 1, (x1, y1), -2)
                            else:
                                Shuriken(load_image('shuriken.png'), 3, 1, (y1 - y) / (x1 - x), (x1, y1), a)
            if not self.pause_game:
                if pygame.sprite.groupcollide(shuriken_group, fire_ball_group, True, True):
                    self.extra_score += 100
                if pygame.sprite.groupcollide(shuriken_group, monsters_group, True, True):
                    self.extra_score += 80
                if pygame.sprite.spritecollide(self.player, fire_ball_group, True) and self.heals > 0:
                    self.heals -= 1
                if pygame.sprite.spritecollide(self.player, monsters_group, True) and self.heals > 0:
                    self.heals -= 1
                dt = self.clock.tick()
                time_since_last_update += dt
                if time_since_last_update > 10:
                    self.lava.update()
                    time_since_last_update = 0
                n = random.randrange(0, 1000)
                if n <= self.fire_chace:
                    if len(fire_ball_group) < self.fire_count:
                        image = random.choice(fire_balls[random.choice(['l', 'r'])])
                        if image in fire_balls['l']:
                            a = -1
                        else:
                            a = 1
                        FireBall(image, 4, 1, a, random.randrange(0, 300), (self.player.rect.x, self.player.rect.y))
                keys = pygame.key.get_pressed()
                if not self.kill:
                    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                        if self.speed_doodle_x > -6:
                            self.speed_doodle_x -= 1
                        self.player.rect.x += self.speed_doodle_x
                    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                        if self.speed_doodle_x < 6:
                            self.speed_doodle_x += 1
                        self.player.rect.x += self.speed_doodle_x
                    else:
                        self.speed_doodle_x *= 0.9
                        self.player.rect.x += self.speed_doodle_x
                if self.heals == 0 and not self.kill:
                    self.kill = True
                    self.player.kill_doodle()
                self.lava.rect.y = self.lava.rect.y - self.lava_speed
                self.player.update_jump()
                monsters_group.update()
                moving_platform_group.update()
                break_platform_group.update(dt)
                shuriken_group.update()
                fire_ball_group.update(dt)
                if (self.player.speed_y > 0 and self.player.pos_y < up_line) or \
                        self.player.pos_y > height - self.player.rect.height:
                    for i in [platform_group, fire_ball_group, monsters_group]:
                        for sprite in i:
                            self.camera.apply(sprite, self.player.real_speed_y)
                            if sprite.rect.y > height + 50 or sprite.rect.y < -200:
                                sprite.kill()
                    self.camera.apply(self.start_pos, self.player.real_speed_y)
                    if self.lava.rect.y < height * 2:
                        self.camera.apply(self.lava, self.player.real_speed_y)
                if int(self.score * self.score_mult) + self.extra_score > self.score_for_update:
                    self.score_for_update += self.score_to_new_update
                    if self.dif == 1:
                        if self.defolt_space < 200:
                            self.defolt_space += 5
                        if self.com_plate >= 5:
                            self.com_plate -= 3
                            self.break_plate += 1
                            self.mov_monst += 1
                            self.move_plate += 1
                        elif self.move_plate > 10:
                            self.break_plate -= 2
                            self.move_plate += 1
                            self.mov_monst += 1
                        self.fire_count += 0.3
                        self.fire_chace += 0.2
                        self.lava_speed += 0.02
                    if self.dif == 2:
                        if self.defolt_space < 200:
                            self.defolt_space += 8
                        if self.com_plate >= 5:
                            self.com_plate -= 3
                            self.break_plate += 0.5
                            self.mov_monst += 1.5
                            self.move_plate += 1
                        elif self.move_plate > 10:
                            self.break_plate -= 2
                            self.move_plate += 1
                            self.mov_monst += 1
                        self.fire_count += 0.4
                        self.fire_chace += 0.4
                        self.lava_speed += 0.03
                    if self.dif == 3:
                        if self.defolt_space < 200:
                            self.defolt_space += 10
                        if self.com_plate >= 5:
                            self.com_plate -= 4
                            self.break_plate += 0.5
                            self.mov_monst += 1.5
                            self.move_plate += 1
                        elif self.move_plate > 10:
                            self.break_plate -= 2.5
                            self.move_plate += 1
                            self.mov_monst += 1.5
                        self.fire_count += 0.5
                        self.fire_chace += 0.5
                        self.lava_speed += 0.05
                if self.score < self.start_pos.rect.y - self.player.rect.y:
                    self.score = self.start_pos.rect.y - self.player.rect.y
                    if self.y_for_new_plate < self.score - self.space:
                        self.y_for_new_plate += self.space
                        if last_obj_is_monst:
                            n = random.randrange(1, int(self.com_plate + self.move_plate + self.break_plate + 1))
                            last_obj_is_monst = False
                        else:
                            n = random.randrange(1, 101)
                        if n <= self.com_plate:
                            CommonPlate(random.randrange(0, width - load_image('common_plate.png').get_width()), 0)
                            self.space = self.defolt_space
                        elif n <= self.com_plate + self.move_plate:
                            MovingPlate(random.randrange(0, width - load_image('moving_plate.png').get_width()), 0)
                            self.space = self.defolt_space + 100
                            last_obj_is_monst = True
                        elif n <= self.com_plate + self.move_plate + self.break_plate:
                            BreakPlate(4, 1,
                                       random.randrange(0, width - load_image('break_plate.png').get_width() // 4), 0)
                            self.space = self.defolt_space
                        elif n <= self.com_plate + self.move_plate + self.break_plate + self.mov_monst:
                            MovingMonster(load_image('moving_monster.png'), 2, 1,
                                          random.randrange(0, width - load_image('moving_monster.png').get_width()),
                                          -20)
                            self.space = self.defolt_space
                            last_obj_is_monst = True
                if not platform_group and not g_o:
                    self.lava.rect.y = height
                    g_o = True
                screen.blit(self.fon, (-100, 0))
                platform_group.draw(screen)
                monsters_group.draw(screen)
                screen.blit(self.player.image, self.player.rect)
                if self.kill:
                    self.stars.update(dt)
                    screen.blit(self.stars.image, (self.stars.rect.x, self.stars.rect.y))
                shuriken_group.draw(screen)
                fire_ball_group.draw(screen)
                screen.blit(self.lava.image, (self.lava.rect.x, self.lava.rect.y))
                screen.blit(self.top_score_line, (0, -10))
                score_text = load_font('Comic Sans MS.ttf', 36).render(
                    str(int(self.score * self.score_mult) + self.extra_score), True, (0, 0, 0))
                heals_count = load_font('Comic Sans MS.ttf', 36).render(str(self.heals) + '×', True, (0, 0, 0))
                y_heals_count = (55 - heals_count.get_height()) // 2
                x_heals_count = 300 - heals_count.get_width()
                screen.blit(heals_count, (x_heals_count, y_heals_count))
                w_score_text = score_text.get_width()
                screen.blit(score_text, (width - w_score_text - 20, 0))
                y_heals_image = (55 - heard.get_height()) // 2
                x_heals_image = 300
                screen.blit(heard, (x_heals_image, y_heals_image))
                buttons_group.draw(screen)
            if self.pause_game:
                screen.blit(self.fon, (0, 0))
                screen.blit(doodle_jump_text, (d_j_t_x, 100))
                screen.blit(pause_text, (pause_x, 220))
                screen.blit(resume.image, (resume.rect.x, resume.rect.y))
                screen.blit(menu.image, (menu.rect.x, menu.rect.y))
            if pygame.sprite.collide_mask(self.player, self.lava):
                return self.game_over
            self.clock.tick(FPS)
            pygame.display.flip()

    def game_over(self):
        for sprite in buttons_group:
            sprite.kill()
        pygame.mixer.stop()
        game_over = load_sound('game_over.mp3')
        game_over.play()
        play = Button(width + 10, height + 10, load_image('play.png'))
        menu = Button(width + 10, height + 10, load_image('menu.png'))
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
        score_text = font2.render(f'score: {int(self.score * self.score_mult) + self.extra_score}',
                                  True, (166, 166, 166))
        x_score_text = (width - score_text.get_width()) // 2
        font3 = load_font('Comic Sans MS.ttf', 30)
        enter_your_name_text = font3.render('enter your name: ', True, (166, 166, 166))
        input_rect = pygame.Rect(20 + enter_your_name_text.get_width(),
                                 200 + game_over_text.get_height() + score_text.get_height(), 205, 50)
        with open('last_name.txt', 'r', encoding='utf-8') as t:
            a = t.read()
            if a:
                user_text = a
            else:
                user_text = 'defolt_name'
        used_rect = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_score(user_text)
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if input_rect.collidepoint(*event.pos):
                            used_rect = True
                        else:
                            used_rect = False
                        if play.rect.collidepoint(*event.pos):
                            self.save_score(user_text)
                            self.del_groups()
                            return self.run
                    if menu.rect.collidepoint(*event.pos):
                        self.save_score(user_text)
                        self.del_groups()
                        return StartWindow
                if event.type == pygame.KEYDOWN and used_rect:
                    if event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode
            if self.lava.rect.y > 0:
                self.lava.rect.y -= 10
            dt = self.clock.tick()
            time_since_last_update += dt
            if time_since_last_update > 10:
                self.lava.update()
                time_since_last_update = 0
            screen.blit(self.fon, (0, 0))
            platform_group.draw(screen)
            screen.blit(self.player.image, self.player.rect)
            screen.blit(self.lava.image, (self.lava.rect.x, self.lava.rect.y))
            if self.lava.rect.y <= 0:
                if opacity < 255:
                    opacity += 10
                s.set_alpha(opacity)
            screen.blit(s, (0, 0))
            if opacity > 255:
                pygame.mixer.stop()
                if play.rect.x > width:
                    play.rect.x = 140
                    play.rect.y = height - 200
                    menu.rect.x = 140
                    menu.rect.y = height - 100
                screen.blit(game_over_text, (x_game_over_text, 200))
                screen.blit(score_text, (x_score_text, 200 + game_over_text.get_height()))
                screen.blit(enter_your_name_text, (20, 200 + game_over_text.get_height() + score_text.get_height()))
                if used_rect:
                    pygame.draw.rect(screen, pygame.color.Color('#a0d6b4'), input_rect, 2)
                else:
                    pygame.draw.rect(screen, pygame.color.Color('#0b596b'), input_rect, 2)
                user_text_blit = font3.render(user_text, True, (166, 166, 166))
                while user_text_blit.get_width() > input_rect.width - 10:
                    user_text = user_text[:-1]
                    user_text_blit = font3.render(user_text, True, (166, 166, 166))
                screen.blit(user_text_blit, (input_rect.x + 10, input_rect.y))
            buttons_group.draw(screen)
            self.clock.tick(FPS)
            pygame.display.flip()

    def del_groups(self):
        for i in all_spite_group:
            i.kill()
        self.__init__(self.dif)

    def save_score(self, user_text):
        con = sqlite3.connect('lider_table.sgl')
        cur = con.cursor()
        if user_text != 'defolt_name':
            a = cur.execute('''
            select score from Scores
                where name = ?
            ''', (user_text,)).fetchall()
            if a:
                if a[0][0] < int(self.score * self.score_mult) + self.extra_score:
                    cur.execute('''
                    update Scores
                    set score = ?
                    where name = ?
                    ''', (int(self.score * self.score_mult) + self.extra_score, user_text))
            else:
                cur.execute('''
                INSERT INTO Scores(name, score) VALUES (?, ?)
                ''', (user_text, int(self.score * self.score_mult) + self.extra_score))
            con.commit()
            con.close()
            with open('last_name.txt', 'w', encoding='utf-8') as f:
                f.write(user_text)
        else:
            with open('last_name.txt', 'w', encoding='utf-8') as f:
                f.write(user_text)


class ScoreWindow:
    def __init__(self):
        self.screen2 = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.update_score()
        self.clock = pygame.time.Clock()
        self.running = True
        self.fon = load_image('fon.png')
        self.top_score = load_image('top-score.png')
        self.back = Button(3, 3, load_image('back.png'))
        self.trash = Button(400, 3, load_image('trash.png'))

    def run_win(self):
        a = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if a + self.height_line > height - 80 and event.button == 4:
                        a -= 15
                    if a < 0 and event.button == 5:
                        a += 15
                    if event.button == 1:
                        if self.back.rect.collidepoint(*event.pos):
                            return StartWindow
                        if self.trash.rect.collidepoint(*event.pos):
                            self.del_bd()
                            self.update_score()
                            a = 0
            screen.blit(self.fon, (-100, 0))
            screen.blit(self.screen2, (0, a + 80))
            screen.blit(self.top_score, (0, 0))
            buttons_group.draw(screen)
            self.clock.tick(FPS)
            pygame.display.flip()

    def update_score(self):
        con = sqlite3.connect('lider_table.sgl')
        cur = con.cursor()
        self.score_list = cur.execute('''select * from Scores
        order by -1 * score''').fetchall()
        con.close()
        self.screen2 = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.height_line = 20
        for i in range(len(self.score_list)):
            score_text_index = str(i + 1)
            score_text_name = str(self.score_list[i][0])
            score_text_score = str(self.score_list[i][1])
            font1 = load_font('Comic Sans MS.ttf', 36)
            index = font1.render(score_text_index, True, (0, 0, 0))
            self.screen2.blit(index, (15, self.height_line))
            name = font1.render(score_text_name, True, (0, 0, 0))
            self.screen2.blit(name, (90, self.height_line))
            score = font1.render(score_text_score, True, (0, 0, 0))
            self.screen2.blit(score, (340, self.height_line))
            self.height_line += 10 + name.get_height()

    def del_bd(self):
        con = sqlite3.connect('lider_table.sgl')
        cur = con.cursor()
        cur.execute('delete from Scores')
        con.commit()
        con.close()


class StartWindow:
    def __init__(self):
        pygame.display.set_caption('doodle jump')
        self.clock = pygame.time.Clock()
        self.running = True
        self.fon = load_image('fon.png')

    def run_win(self):
        if not pygame.mixer.get_busy():
            fon_sound = load_sound('fon_music.mp3')
            fon_sound.set_volume(0.2)
            fon_sound.play(loops=-1)
        font = load_font('Comic Sans MS.ttf', 50)
        doodle_jump_text = load_font('Comic Sans MS.ttf', 70).render('Doodle jump', True, (255, 0, 0))
        doodle_jump_text = pygame.transform.rotate(doodle_jump_text, 20)
        d_j_t_x = (width - doodle_jump_text.get_width()) // 2
        buttons = []
        for h, text in [(700, "Exit"), (600, "Score"), (500, "Play")]:
            text = font.render(text, True, (0, 0, 0))
            text_x = width // 2 - text.get_width() // 2
            text_y = h
            text_w = text.get_width()
            text_h = text.get_height()
            rect = pygame.Rect(text_x, text_y, text_w, text_h)
            buttons.append((text, rect))
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if buttons[0][1].collidepoint(*event.pos):
                            return None
                        if buttons[1][1].collidepoint(*event.pos):
                            for i in all_spite_group:
                                i.kill()
                            return ScoreWindow
                        if buttons[2][1].collidepoint(*event.pos):
                            return DifficultWindow
            screen.blit(self.fon, (-100, 0))
            for i in buttons:
                screen.blit(*i)
            screen.blit(doodle_jump_text, (d_j_t_x, 50))
            self.clock.tick(FPS)
            pygame.display.flip()


class DifficultWindow:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.fon = load_image('fon.png')

    def run_win(self):
        buttons = []
        font = load_font('Comic Sans MS.ttf', 50)
        for h, text in [(800, 'Back'), (500, "Normal"), (600, "Hard"), (700, "Very Hard")]:
            text = font.render(text, True, (0, 0, 0))
            text_y = h
            text_x = (width - text.get_width()) // 2
            text_w = text.get_width()
            text_h = text.get_height()
            rect = pygame.Rect(text_x, text_y, text_w, text_h)
            buttons.append((text, rect))
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if buttons[1][1].collidepoint(*event.pos):
                            return Game, 1
                        if buttons[2][1].collidepoint(*event.pos):
                            for i in all_spite_group:
                                i.kill()
                            return Game, 2
                        if buttons[3][1].collidepoint(*event.pos):
                            return Game, 3
                        if buttons[0][1].collidepoint(*event.pos):
                            return StartWindow
            screen.blit(self.fon, (-100, 0))
            for i in buttons:
                screen.blit(*i)
            self.clock.tick(FPS)
            pygame.display.flip()
