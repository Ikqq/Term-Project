import pygame


class Background_class:
    def __init__(self, image_path, screen_width, screen_height, speed=3):
        self.speed = speed
        self.width = screen_width
        self.height = screen_height
        view_image = pygame.image.load(image_path).convert_alpha()
        self.image1 = pygame.transform.scale(view_image, (screen_width, screen_height))
        self.image2 = pygame.transform.flip(self.image1, True, False)
        self.x1 = 0
        self.x2 = self.width

    def update(self):
        self.x1 -= self.speed
        self.x2 -= self.speed

        if self.x1 <= -self.width:
            self.x1 = self.x2 + self.width

        if self.x2 <= -self.width:
            self.x2 = self.x1 + self.width

    def draw(self, screen):
        screen.blit(self.image1, (self.x1, 0))
        screen.blit(self.image2, (self.x2, 0))
