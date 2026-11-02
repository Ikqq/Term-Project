import pygame
import sys
import os

# 1. เริ่มต้น Pygame
pygame.init()

# ตั้งค่าหน้าจอ
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Highway - Move Character")

clock = pygame.time.Clock()

# 2. โหลดรูปภาพจากโฟลเดอร์ assets ตรงๆ
image_path = os.path.join('gamepicture', 'pixelhorse.png')
player_image_original = pygame.image.load(image_path).convert_alpha()

# ปรับขนาดรูปภาพ (กว้าง 80, สูง 40 พิกเซล)
target_width = 80
target_height = 40
player_image = pygame.transform.scale(player_image_original, (target_width, target_height))

# --- ข้อมูลตัวละคร ---
player_width = target_width
player_height = target_height

# ตำแหน่งเริ่มต้น (อยู่ฝั่งซ้ายของจอ และกึ่งกลางแนวตั้ง)
player_x = 100
player_y = (SCREEN_HEIGHT // 2) - (player_height // 2)

# ความเร็วในการเคลื่อนที่ขึ้น-ลง
player_speed = 5

COLOR_BG = (30, 30, 40) # สีพื้นหลัง

# --- GAME LOOP ---
running = True
while running:
    # A. รับ Event การกดปุ่ม
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # กด ESC เพื่อออกเกม
                running = False

    # B. Update (คำนวณตำแหน่งใหม่ตามการกดปุ่มค้างไว้)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] or keys[pygame.K_w]:     # กดลูกศรขึ้น หรือ W
        player_y -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:   # กดลูกศรลง หรือ S
        player_y += player_speed

    # ป้องกันไม่ให้รถขับตกขอบจอ (บนสุดและล่างสุด)
    if player_y < 0:
        player_y = 0
    elif player_y > SCREEN_HEIGHT - player_height:
        player_y = SCREEN_HEIGHT - player_height

    # C. Draw (วาดภาพลงจอ)
    screen.fill(COLOR_BG)
    screen.blit(player_image, (player_x, player_y))

    # D. Display Update & FPS Clock
    pygame.display.flip()
    clock.tick(60)

# ออกจากเกมอย่างปลอดภัย
pygame.quit()
sys.exit()