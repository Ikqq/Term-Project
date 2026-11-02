import pygame 
import sys
import os
import random

# Zone of Class
class player_class: #Player Class
    def __init__(self,x,y,image_path,scale_factor=0.5,speed=5):
        car_image = pygame.image.load(image_path).convert_alpha()

        og_width = car_image.get_width()
        og_height = car_image.get_height()

        self.width = int(og_width*scale_factor)
        self.height = int(og_height*scale_factor)

        self.image = pygame.transform.scale(car_image,(self.width,self.height))
        self.mask = pygame.mask.from_surface(self.image)

        self.x = x
        self.y = y
        self.speed = speed

        self.current_lane = 1
        self.lanes_y = []

    def set_lane(self,screen_height) :
        top_of_road = screen_height//2
        road_height = screen_height//2
        lane_height = road_height//3

        self.lanes_y = [
            top_of_road + lane_height//2 -self.height//2,
            top_of_road + 1*lane_height + lane_height//2-self.height//2,
            top_of_road + 2*lane_height + lane_height//2-self.height//2 
        ]

        self.y = self.lanes_y[self.current_lane]

    def move_up (self):
        if self.current_lane > 0 :
            self.current_lane-=1
            self.y = self.lanes_y[self.current_lane]

    def move_down (self) :
        if self.current_lane <2 :
            self.current_lane+=1
            self.y = self.lanes_y[self.current_lane]

    def draw(self,screen) :
        screen.blit(self.image, (self.x, self.y))

class Obstacle_class : #Obstacle Class
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
            top_of_road + 2 * lane_height + lane_height // 2 - self.height // 2 
        ]

        self.speed = speed
        self.is_active = False

    def spawn(self):
        self.y = random.choice(self.lanes_y)
        self.x = self.screen_width
        self.is_active = True

    def update(self):
        if self.is_active :
            self.x -= self.speed
            if self.x < -self.width:
                self.is_active = False

    def draw(self, screen):
        if self.is_active :
            screen.blit(self.obs_image, (self.x, self.y))

class Background_class:
    def __init__(self, image_path, screen_width, screen_height, speed=3):
        self.speed = speed
        self.width = screen_width
        self.height = screen_height
        view_image = pygame.image.load(image_path).convert_alpha()
        self.image1 = pygame.transform.scale(view_image,(screen_width,screen_height))
        self.image2 = pygame.transform.flip(self.image1,True,False)
        self.x1 = 0
        self.x2 = self.width

    def update(self): 
        self.x1 -= self.speed
        self.x2 -= self.speed

        if self.x1 <= -self.width :
            self.x1 = self.x2 + self.width

        if self.x2 <= -self.width :
            self.x2 = self.x1 + self.width

    def draw(self,screen) :
        screen.blit(self.image1,(self.x1,0))
        screen.blit(self.image2,(self.x2,0))

class HP:
    def __init__(self,heart_path1,heart_path2, max_hp):
        self.hp = max_hp
        heart_image = pygame.image.load(heart_path1).convert_alpha()
        grey_heart_image = pygame.image.load(heart_path2).convert_alpha()
        og_width = heart_image.get_width()
        og_height = heart_image.get_height()

        self.width = int(og_width*0.05)
        self.height = int(og_height*0.05)
        self.width_2 = int(og_width*0.05)
        self.height_2 = int(og_height*0.05)
        self.image = pygame.transform.scale(heart_image,(self.width,self.height))
        self.image2 = pygame.transform.scale(grey_heart_image,(self.width,self.height))
        
        self.spacing = 10
        self.start_x = 30
        self.start_y = 30
    def draw(self,screen) :
        for i in range(0,3) :
            x_pos = self.start_x + (i*(self.width + self.spacing))
            if i < self.hp :
                screen.blit(self.image,(x_pos,self.start_y))
            else :
                screen.blit(self.image2,(x_pos,self.start_y))

# Zone of main
pygame.init()
pygame.display.set_caption("Pixel Car 2D : OOP Edition")

info_screen = pygame.display.Info()
screen_width = info_screen.current_w
screen_height = info_screen.current_h

screen = pygame.display.set_mode((screen_width,screen_height),pygame.FULLSCREEN)
clock = pygame.time.Clock()
color_BG = (30,30,40)

#player picture
image_path = os.path.join('gamepicture','car.png')
start_x = 50
start_y = screen_height//2 

#obstacle picture
obstacle_path = os.path.join('gamepicture','obstacle1.png')

#background picture
background_path = os.path.join('gamepicture','view3.jpg')

#heart picture
heart_path = os.path.join('gamepicture','heart.png')
heart_path2 = os.path.join('gamepicture','grey_heart.png')

#setup our game
player = player_class(start_x,start_y,image_path,0.3,10)
player.set_lane(screen_height)

obstacle = Obstacle_class(obstacle_path,screen_width,screen_height,0.05,15)
spawn_obstacles_time = 500 ## 5 Second
last_spawn_time = pygame.time.get_ticks()

background = Background_class(background_path,screen_width,screen_height,5)

player_hp = HP(heart_path,heart_path2,3)


#Game Loop
running = True
while(running) :
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
    keys = pygame.key.get_pressed()
    
    
    ## การชน
    # offset_of_obstcle = (obstacle.x - player.x, obstacle.y - player.y)
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time >= spawn_obstacles_time :
        if not obstacle.is_active :
            obstacle.spawn()
            last_spawn_time = current_time

    obstacle.update()
    background.update()

    if obstacle.is_active:
        offset = (obstacle.x - player.x , obstacle.y - player.y)
        if player.mask.overlap(obstacle.mask,offset) :
            player_hp.hp -= 1
            obstacle.is_active = False

            if player_hp.hp <= 0 :
                running = False

    screen.fill(color_BG) #เคลียร์จอก่อนวาดรูปใหม่ทุกเฟรมเรท
    background.draw(screen)
    player_hp.draw(screen)
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
    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()