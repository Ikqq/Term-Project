import pygame
from Obstacle_class import Obstacle_class


class Coin_class(Obstacle_class):
    def __init__(self, coin_paths, screen_width, screen_height, scale_factor=0.08, speed=5):
        super().__init__(coin_paths[0], screen_width, screen_height, scale_factor, speed)

        self.images = []
        for path in coin_paths:
            img = pygame.image.load(path).convert_alpha()
            self.images.append(pygame.transform.scale(img, (self.width, self.height)))

        self.current_frame = 0
        self.animation_speed = 0.15
        self.image = self.images[0]
        self.obs_image = self.image 
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if self.is_active:
            super().update()

            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.images):
                self.current_frame = 0

            self.image = self.images[int(self.current_frame)]
            self.obs_image = self.image 
            self.mask = pygame.mask.from_surface(self.image)
