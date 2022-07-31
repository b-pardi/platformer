import pygame

class jumper():
    def __init__(self, loc, jumper_img):
        self.loc = loc
        self.img = jumper_img
        self.width = jumper_img.get_width()
        self.height = jumper_img.get_height()

    def render(self, surface, scroll):
        surface.blit(self.img, (self.loc[0] - scroll[0], self.loc[1] - scroll[1]))

    def get_rect(self):
        rect = pygame.Rect(self.loc[0], self.loc[1], self.width, self.height)
        return rect

    def collision_test(self, rect):
        jumper_rect = self.get_rect()
        return jumper_rect.colliderect(rect)