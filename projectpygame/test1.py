import pygame

pygame.init()

pygame.display.set_caption("Pixel Car 2D Draft 1")

#white = (255,255,255)
red = (255,0,0)

screen = pygame.display.set_mode((800,600))
screen.fill((255,255,255))
pygame.draw.rect(screen,red,(100,100,100,50))
pygame.draw.circle(screen,(0,0,0),(400,80),50,3)

sys_font = pygame.font.SysFont("arial",20)
message_text = sys_font.render("Hello",True,red)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()
    screen.blit(message_text,(200,100))
pygame.quit()