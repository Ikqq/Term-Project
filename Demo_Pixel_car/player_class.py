import pygame


class player_class:  # Player Class
    def __init__(self, x, y, image_paths, scale_factor=0.5, speed=5):
        self.images = []
        for path in image_paths:
            img = pygame.image.load(path).convert_alpha()

            bounding_rect = img.get_bounding_rect()
            cropped_img = img.subsurface(bounding_rect)

            w = int(cropped_img.get_width() * scale_factor)
            h = int(cropped_img.get_height() * scale_factor)
            scaled_img = pygame.transform.scale(cropped_img, (w, h))
            self.images.append(scaled_img)

        self.width = self.images[0].get_width()
        self.height = self.images[0].get_height()

        self.current_frame = 0          
        self.animation_speed = 0.09    

        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)

        self.x = x
        self.y = y
        self.speed = speed

        self.current_lane = 1
        self.lanes_y = []

    def set_lane(self, screen_height):
        top_of_road = screen_height // 2
        road_height = screen_height // 2
        lane_height = road_height // 3

        self.lanes_y = [
            top_of_road + lane_height // 2 - self.height // 2,
            top_of_road + 1 * lane_height + lane_height // 2 - self.height // 2,
            top_of_road + 2 * lane_height + lane_height // 2 - self.height // 2,
        ]

        self.y = self.lanes_y[self.current_lane]

    def move_up(self):
        if self.current_lane > 0:
            self.current_lane -= 1
            self.y = self.lanes_y[self.current_lane]

    def move_down(self):
        if self.current_lane < 2:
            self.current_lane += 1
            self.y = self.lanes_y[self.current_lane]

    def update(self):
        self.current_frame += self.animation_speed

        if self.current_frame >= len(self.images):
            self.current_frame = 0

        self.image = self.images[int(self.current_frame)]
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
