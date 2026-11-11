import pygame


class HP:
    def __init__(self, heart_path1, heart_path2, max_hp):
        self.hp = max_hp
        heart_image = pygame.image.load(heart_path1).convert_alpha()
        grey_heart_image = pygame.image.load(heart_path2).convert_alpha()
        og_width = heart_image.get_width()
        og_height = heart_image.get_height()

        self.width = int(og_width * 0.05)
        self.height = int(og_height * 0.05)

        self.width_2 = int(og_width * 0.05)
        self.height_2 = int(og_height * 0.05)

        self.image = pygame.transform.scale(heart_image, (self.width, self.height))
        self.image2 = pygame.transform.scale(grey_heart_image, (self.width, self.height))

        self.spacing = 10
        self.start_x = 30
        self.start_y = 30

    def draw(self, screen):
        for i in range(0, 3):
            x_pos = self.start_x + (i * (self.width + self.spacing))
            if i < self.hp:
                screen.blit(self.image, (x_pos, self.start_y))
            else:
                screen.blit(self.image2, (x_pos, self.start_y))
