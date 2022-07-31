import pygame

BLACK = (255, 255, 255)
FONT = pygame.font.SysFont(None, 20)



def main_menu(screen):
    while 1:
        screen.fill((0,200,200))
        draw_text('main menu', FONT, BLACK, screen, 20, 20)

        for event