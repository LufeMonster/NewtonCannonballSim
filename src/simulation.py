import pygame
import math

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

projectile_pos_x = 640
projectile_pos_y = 180

projectile_vel_x = 0.5
projectile_vel_y = 0

projectile_acc_x = 0
projectile_acc_y = 0

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE
    
    pygame.draw.circle(screen, (0, 0, 255), (640, 360), 8)
    
    pygame.draw.circle(screen, (255, 0, 0), (projectile_pos_x, projectile_pos_y), 32)
    projectile_pos_x += projectile_vel_x
    projectile_pos_y += projectile_vel_y
    
    projectile_vel_x += projectile_acc_x
    projectile_vel_y += projectile_acc_y
    
    projectile_acc_x = -0.001 * ((projectile_pos_x - 640) / math.sqrt((projectile_pos_x - 640) ** 2 + (projectile_pos_y - 360) ** 2))
    projectile_acc_y = -0.001 * ((projectile_pos_y - 360) / math.sqrt((projectile_pos_x - 640) ** 2 + (projectile_pos_y - 360) ** 2))
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()