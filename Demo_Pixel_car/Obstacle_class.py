import pygame
import random


class Obstacle_class:  # Obstacle Class
    def __init__(self, obstacle_path, screen_width, screen_height, scale_factor=0.5, speed=3):
        obstacle1_image = pygame.image.load(obstacle_path).convert_alpha()
        og_width = obstacle1_image.get_width()
        og_height = obstacle1_image.get_height()

        self.width = int(og_width * scale_factor)
        self.height = int(og_height * scale_factor)

        self.obs_image = pygame.transform.scale(obstacle1_image, (self.width, self.height))
        self.mask = pygame.mask.from_surface(self.obs_image)

        self.screen_width = screen_width
        top_of_road = screen_height // 2
        road_height = screen_height // 2
        lane_height = road_height // 3
        self.lanes_y = [
            top_of_road + lane_height // 2 - self.height // 2,
            top_of_road + 1 * lane_height + lane_height // 2 - self.height // 2,
            top_of_road + 2 * lane_height + lane_height // 2 - self.height // 2,
        ]

        self.speed = speed
        self.is_active = False

    def spawn(self):
        self.y = random.choice(self.lanes_y)
        self.x = self.screen_width
        self.is_active = True

    def update(self):
        if self.is_active:
            self.x -= self.speed
            if self.x < -self.width:
                self.is_active = False

    def draw(self, screen):
        if self.is_active:
            screen.blit(self.obs_image, (self.x, self.y))
