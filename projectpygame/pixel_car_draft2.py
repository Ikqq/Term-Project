import pygame
import sys
import os

pygame.init()
pygame.display.set_caption("Pixel Car 2D : draft 2")

info_screen = pygame.display.Info()
screen_width = info_screen.current_w
screen_height = info_screen.current_h 

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# our characters
image_path = os.path.join('gamepicture', 'pixelhorse.png')
horse_image = pygame.image.load(image_path).convert_alpha()

# size of og picture
og_width = horse_image.get_width()
og_height = horse_image.get_height()

# size in display mode (Integer Scaling คูณ 3 เท่าเพื่อความคมชัด)
scale_factor = 0.5
target_width = int(og_width * scale_factor)
target_height = int(og_height * scale_factor)
player_image = pygame.transform.scale(horse_image, (target_width, target_height))

player_width = target_width
player_height = target_height
player_x = 50 
player_y = (screen_height // 2) - (player_height // 2)
speed = 5

# left right horse face
player_image_right = player_image
player_image_left = pygame.transform.flip(player_image,True,False)
facing = True


COLOR_BG = (30, 30, 40)

running = True
while running:
    # key action
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False 

    # up down left right of our characters
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] or keys[pygame.K_w]: # กดลูกศรขึ้น หรือ W
        player_y -= speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: # กดลูกศรลง หรือ S
        player_y += speed
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: # กดลูกศรซ้าย หรือ A
        player_x -= speed
        facing = False
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: # หกลูกศรขวา หรือ D
        player_x += speed
        facing = True

    # protect about up_bound, down_bound
    if player_y < 0:
        player_y = 0
    elif player_y > screen_height - player_height:
        player_y = screen_height - player_height
    elif player_x > screen_width - player_width:
        player_x = screen_width - player_width
    elif player_x < 0 :
        player_x = 0

    # display our characters to screen
    screen.fill(COLOR_BG)  # ต้องใส่ screen.fill ไว้ในลูป เพื่อล้างภาพเก่าทุกเฟรม
    if facing :
        screen.blit(player_image_right, (player_x, player_y))
    else :
        screen.blit(player_image_left, (player_x, player_y))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()