import pygame
import sys
import os

from player_class import player_class
from Obstacle_class import Obstacle_class
from Coin_class import Coin_class
from Background_class import Background_class
from HP import HP

os.chdir(os.path.dirname(os.path.abspath(__file__)))
point = 0

# Zone of main
pygame.init()
pygame.display.set_caption("Pixel Car 2D : OOP Edition")

info_screen = pygame.display.Info()
screen_width = info_screen.current_w
screen_height = info_screen.current_h

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
clock = pygame.time.Clock()
color_BG = (30, 30, 40)

# player picture
car_images = [
    os.path.join('gamepicture', 'car.1.png'),
    # os.path.join('gamepicture', 'car.2.png'),
    # os.path.join('gamepicture', 'car.3.png'),
    # os.path.join('gamepicture', 'car.4.png')
]

start_x = 50
start_y = screen_height // 2

# obstacle picture
obstacle_path = os.path.join('gamepicture', 'obstacle1.png')

# background picture
background_path = os.path.join('gamepicture', 'view3.jpg')

# heart picture
heart_path = os.path.join('gamepicture', 'heart.png')
heart_path2 = os.path.join('gamepicture', 'grey_heart.png')

# setup our game
player = player_class(start_x, start_y, car_images, 0.3, 10)
player.set_lane(screen_height)

obstacle = Obstacle_class(obstacle_path, screen_width, screen_height, 0.05, 15)
spawn_obstacles_time = 500  # milliseconds
last_spawn_time = pygame.time.get_ticks()

# รวม Path รูปภาพเหรียญ 3 เฟรม
coin_images = [
    os.path.join('gamepicture', 'coin1.png'),
    os.path.join('gamepicture', 'coin2.png'),
    os.path.join('gamepicture', 'coin3.png'),
]

# สร้างวัตถุเหรียญและตั้งค่าสปอว์น
coin = Coin_class(coin_images, screen_width, screen_height, 0.5, 13)
spawn_coin_time = 1000  # milliseconds
last_coin_spawn_time = pygame.time.get_ticks()

coin_icon_path = os.path.join('gamepicture', 'Coin1.png')
coin_icon_raw = pygame.image.load(coin_icon_path).convert_alpha()
coin_icon = pygame.transform.scale(coin_icon_raw, (100, 100))

font_score = pygame.font.SysFont("Arial", 30, bold=True)

background = Background_class(background_path, screen_width, screen_height, 5)

player_hp = HP(heart_path, heart_path2, 3)



# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                player.move_up()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                player.move_down()

    current_time = pygame.time.get_ticks()

    if current_time - last_spawn_time >= spawn_obstacles_time:
        if not obstacle.is_active:
            obstacle.spawn()
            last_spawn_time = current_time

    if current_time - last_coin_spawn_time >= spawn_coin_time:
        if not coin.is_active:
            coin.spawn()
            last_coin_spawn_time = current_time

    player.update()
    coin.update()
    obstacle.update()
    background.update()

    # การชนกับสิ่งกีดขวาง
    if obstacle.is_active:
        offset = (obstacle.x - player.x, obstacle.y - player.y)
        if player.mask.overlap(obstacle.mask, offset):
            player_hp.hp -= 1
            obstacle.is_active = False

            if player_hp.hp <= 0:
                running = False

    # การชนกับเหรียญ
    if coin.is_active:
        offset_coin = (coin.x - player.x, coin.y - player.y)
        if player.mask.overlap(coin.mask, offset_coin):
            point += 1
            print(point)
            coin.is_active = False

    screen.fill(color_BG)  # เคลียร์จอก่อนวาดรูปใหม่ทุกเฟรม

    coin.draw(screen)
    background.draw(screen)
    player_hp.draw(screen)

    score_surface = font_score.render(f"x {point}", True, (255, 215, 0))
    screen.blit(score_surface, (screen_width - 70, 30))
    screen.blit(coin_icon, (screen_width - 150, -5))

    # วาดเส้นแบ่งเลนถนน
    road_top = screen_height // 2
    road_height = screen_height // 2
    lane_height = road_height // 3
    line1_y = road_top + lane_height
    line2_y = road_top + (lane_height * 2)
    line_color = (200, 200, 200)
    pygame.draw.line(screen, line_color, (0, line1_y), (screen_width, line1_y), 3)
    pygame.draw.line(screen, line_color, (0, line2_y), (screen_width, line2_y), 3)

    obstacle.draw(screen)
    coin.draw(screen)
    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
