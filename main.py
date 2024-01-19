from Windows import StartWindow
import pygame

if __name__ == '__main__':
    game = StartWindow().run_win()
    while game is not None:
        if type(game) is tuple:
            game, dif = game
            game = game(dif).run_win()
        else:
            game = game().run_win()
    pygame.quit()
