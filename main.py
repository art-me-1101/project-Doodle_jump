from Windows import Start_window
import pygame

if __name__ == '__main__':
    game = Start_window().run_win()
    while game is not None:
        if type(game) == tuple:
            game, dif = game
            game = game(dif).run_win()
        else:
            game = game().run_win()
    pygame.quit()
