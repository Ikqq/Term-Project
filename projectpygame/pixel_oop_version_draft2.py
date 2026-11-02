import pygame 
import sys
import os
import random

# Zone of Class
class player_class: #Player Class
    def __init__(self,x,y,image_path,scale_factor=0.5,speed=5):
        horse_image = pygame.image.load(image_path).convert_alpha()
        og_width = horse_image.get_width()
        og_height = horse_image.get_height()

        self.width = int(og_width*scale_factor)
        self.height = int(og_height*scale_factor)

        self.image_right = pygame.transform.scale(horse_image,(self.width,self.height))
        self.image_left = pygame.transform.flip(self.image_right, True, False)

        self.x = x
        self.y = y
        self.speed = speed
        self.facing_right = True

    def handle_input(self, keys,screen_height) :
        if keys[pygame.K_UP] or keys[pygame.K_w] :
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s] :
            self.y += self.speed

        if self.y <screen_height//2 - self.height//1.7 :
            self.y = screen_height//2 - self.height//1.7
        elif self.y > screen_height-self.height//1.2 :
            self.y = screen_height-self.height//1.2

    def draw(self,screen) :
        if self.facing_right:
            screen.blit(self.image_right, (self.x, self.y))
        else:
            screen.blit(self.image_left, (self.x, self.y))

class Obstacle_class : #Obstacle Class
    def __init__(self,obstacle_path, screen_width, screen_height, scale_factor = 0.5, speed=1):
        obstacle1_image = pygame.image.load(obstacle_path).convert_alpha()
        og_width = obstacle1_image.get_width()
        og_height = obstacle1_image.get_height()

        self.width = int(og_width*scale_factor)
        self.height = int(og_height*scale_factor)

        self.obs_image = pygame.transform.scale(obstacle1_image,(self.width,self.height))

        self.x = screen_width
        self.y = random.randint(screen_height//2+self.height,screen_height-self.height)
        self.speed = speed

    def update(self, screen_width, screen_height):
        self.x -= self.speed
        if self.x < -self.width :
            self.x = screen_width
            self.y = random.randint(screen_height//2+self.height,screen_height-self.height)

    def draw(self,screen) :
        screen.blit(self.obs_image,(self.x,self.y))

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
start_x = 100
start_y = screen_height//2 

#obstacle picture
obstacle_path = os.path.join('gamepicture','obstacle1.png')

#background picture
background_path = os.path.join('gamepicture','view3.jpg')

#heart picture
heart_path = os.path.join('gamepicture','heart.png')
heart_path2 = os.path.join('gamepicture','grey_heart.png')

player = player_class(start_x,start_y,image_path,0.4,10)
obstacle = Obstacle_class(obstacle_path,screen_width,screen_height,0.05,15)
background = Background_class(background_path,screen_width,screen_height,5)
player_hp = HP(heart_path,heart_path2,1)

#Game Loop
running = True
while(running) :
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    keys = pygame.key.get_pressed()
    player.handle_input(keys,screen_height)
    obstacle.update(screen_width,screen_height)
    background.update()

    screen.fill(color_BG) #เคลียร์จอก่อนวาดรูปใหม่ทุกเฟรมเรท
    background.draw(screen)
    obstacle.draw(screen)
    player.draw(screen)
    player_hp.draw(screen)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()