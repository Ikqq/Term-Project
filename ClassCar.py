import pygame
import os
import random
os.chdir(os.path.dirname(os.path.abspath(__file__)))

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT))
clock = pygame.Clock()
font = pygame.font.SysFont("Arial",70,bold=True)
Program = True
speed_door = 150
delta_time = 0

class Background():
        def __init__(self,x,y):
                self.image = pygame.image.load("view3.jpg").convert_alpha()
                self.image = pygame.transform.scale(self.image,(SCREEN_WIDTH,SCREEN_HEIGHT))
                self.rect = self.image.get_rect(topleft = (x,y))
                self.x = float(x)
                
        def update(self,deltatime):
                self.x -= 60 * deltatime
                self.rect.left = int(self.x) 
                if self.rect.right < 0:
                        self.x = SCREEN_WIDTH
                        self.rect.left = SCREEN_WIDTH
    
        def draw(self):
                screen.blit(self.image,self.rect)
                pygame.draw.line(screen,"White",(0,480),(SCREEN_WIDTH,480))
                pygame.draw.line(screen,"White",(0,600),(SCREEN_WIDTH,600))

class obstacles(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("cone.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(100,100))
        self.image = pygame.transform.flip(self.image,True,False)
        pos_cone = [420,540,660]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH,random.choice(pos_cone)))
        self.mask_cone = pygame.mask.from_surface(self.image)
        self.reset()

    def reset(self):
        pos_cone = [420,540,660]
        self.rect.center = (SCREEN_WIDTH, random.choice(pos_cone))  
        
    def update(self,speed_door,delta_time):
        self.rect.left -= speed_door * delta_time
        if self.rect.right < -50:
                self.reset()
                
    def draw(self):
        screen.blit(self.image,self.rect)

class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("images.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(100,100))
        self.image = pygame.transform.flip(self.image,True,False)
        self.rect = self.image.get_rect(center = (100,540))
        self.mask_car = pygame.mask.from_surface(self.image)
        self.hp_car = 3
        self.alive = True
        
    def update(self,events):
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

    def check_collision(self,cones):
        hits = pygame.sprite.spritecollide(self,cones,False,pygame.sprite.collide_mask)
        if hits:
                self.hp_car -= 1
                print("Hit")
                for cone in hits:
                        cone.reset()
                        
                if self.hp_car <= 0:
                        global Program
                        self.alive = False
                        print("Game Over")
                        Program = False
                        
    def draw(self):
        screen.blit(self.image,self.rect)       


if __name__ == "__main__":
        back1 = Background(0,0)
        back2 = Background(SCREEN_WIDTH,0)
        
        cone = obstacles()
        cones = pygame.sprite.Group()
        cones.add(cone)
        
        car = Car()
        
        while Program:
                events = pygame.event.get()
                
                for event in events:
                        if event.type == pygame.QUIT:
                                Program = False
                        
                back2.update(delta_time)
                back1.update(delta_time)
                
                car.update(events)
                cone.update(speed_door,delta_time)
                
                car.check_collision(cones)
                
                screen.fill("Black")
                back1.draw()
                back2.draw()
                car.draw()
                cone.draw()
                
                
                pygame.display.flip()
                
                delta_time = clock.tick(60) / 1000

        pygame.quit()