import pygame

if __name__ == '__main__':
    pygame.init()
    size = width, height = 1000, 700
    screen = pygame.display.set_mode(size)
    running = True
    fps = 60
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(pygame.Color('black'))
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
