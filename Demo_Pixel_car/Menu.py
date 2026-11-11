import os
import random

import pygame

os.chdir(os.path.dirname(os.path.abspath(__file__)))

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 70, bold=True)
Program = True
speed_door = 200
delta_time = 0
state = "menu"

back1 = None
back2 = None
cone = None
cones = None
car = None
menu = None
game_over_menu = None


class PixelMenu:
    def __init__(self, title, actions):
        self.title = title
        self.actions = actions
        self.title_font = pygame.font.SysFont("Courier New", 54, bold=True)
        self.btn_font = pygame.font.SysFont("Courier New", 24, bold=True)

    def update(self, events):
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, (_, action) in enumerate(self.actions):
                    rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, 330 + i * 90, 280, 52)
                    if rect.collidepoint(mouse):
                        action()
                        return

    def draw(self, surface):
        surface.fill((10, 13, 21))
        pygame.draw.rect(surface, (28, 28, 34), (90, 70, SCREEN_WIDTH - 180, SCREEN_HEIGHT - 140), 4)
        pygame.draw.rect(surface, (18, 18, 26), (110, 90, SCREEN_WIDTH - 220, SCREEN_HEIGHT - 180), 2)

        title = self.title_font.render(self.title, True, (255, 245, 210))
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 160)))

        for i, (label, _) in enumerate(self.actions):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, 330 + i * 90, 280, 52)
            hover = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(surface, (18, 24, 39), rect)
            pygame.draw.rect(surface, (255, 209, 102) if hover else (104, 225, 203), rect, 3)
            btn = self.btn_font.render(label, True, (245, 245, 245))
            surface.blit(btn, btn.get_rect(center=rect.center))


class Background:
    def __init__(self, x, y):
        self.image = pygame.image.load("view3.jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = float(x)

    def update(self, deltatime):
        self.x -= (100 + speed_door * 0.9) * deltatime
        self.rect.left = int(self.x)
        if self.rect.right < 0:
            self.x = SCREEN_WIDTH
            self.rect.left = SCREEN_WIDTH

    def draw(self):
        screen.blit(self.image, self.rect)
        pygame.draw.line(screen, "White", (0, 480), (SCREEN_WIDTH, 480))
        pygame.draw.line(screen, "White", (0, 600), (SCREEN_WIDTH, 600))


class obstacles(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("obstacle1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.image = pygame.transform.flip(self.image, True, False)
        pos_cone = [420, 540, 660]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH, random.choice(pos_cone)))
        self.mask_cone = pygame.mask.from_surface(self.image)
        self.reset()

    def reset(self):
        pos_cone = [420, 540, 660]
        self.rect.center = (SCREEN_WIDTH, random.choice(pos_cone))

    def update(self, speed_door, delta_time):
        self.rect.left -= speed_door * delta_time * 2.2
        if self.rect.right < -50:
            self.reset()

    def draw(self):
        screen.blit(self.image, self.rect)


class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("car.1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=(100, 540))
        self.mask_car = pygame.mask.from_surface(self.image)
        self.hp_car = 3
        self.alive = True

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.rect.y -= 120
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.rect.y += 120

        if self.rect.y < 420:
            self.rect.y = 380

        if self.rect.y > 600:
            self.rect.y = 620

    def check_collision(self, cones):
        hits = pygame.sprite.spritecollide(
            self, cones, False, pygame.sprite.collide_mask
        )
        if hits:
            self.hp_car -= 1
            print("Hit")
            for cone in hits:
                cone.reset()

            if self.hp_car <= 0:
                self.alive = False
                print("Game Over")
                set_game_over()

    def draw(self):
        screen.blit(self.image, self.rect)


def set_game_over():
    global state
    state = "gameover"


def quit_game():
    global Program
    Program = False


def start_game():
    global state, back1, back2, cone, cones, car, speed_door, delta_time
    state = "playing"
    speed_door = 700
    delta_time = 0
    back1 = Background(0, 0)
    back2 = Background(SCREEN_WIDTH, 0)
    cone = obstacles()
    cones = pygame.sprite.Group()
    cones.add(cone)
    car = Car()


def create_menus():
    global menu, game_over_menu

    menu = PixelMenu("CAR GAME", [("START", start_game), ("QUIT", quit_game)])
    game_over_menu = PixelMenu("CRASHED", [("RETRY", start_game), ("QUIT", quit_game)])


if __name__ == "__main__":
    create_menus()

    while Program:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                Program = False

        screen.fill("Black")

        if state == "menu":
            menu.update(events)
            menu.draw(screen)

        elif state == "playing":
            speed_door = min(speed_door + 60 * delta_time, 1200)
            back2.update(delta_time)
            back1.update(delta_time)

            car.update(events)
            cone.update(speed_door, delta_time)

            car.check_collision(cones)

            back1.draw()
            back2.draw()
            car.draw()
            cone.draw()

        elif state == "gameover":
            game_over_menu.update(events)
            game_over_menu.draw(screen)

        pygame.display.flip()
        delta_time = clock.tick(60) / 1000

    pygame.quit()