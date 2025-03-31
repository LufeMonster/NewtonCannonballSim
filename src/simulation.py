import pygame
import math

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

class Projectile:
    def __init__(self, pos_x, pos_y, vel_x, vel_y, acc_x, acc_y, size, color):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.size = size
        self.color = color
    
    def move(self, dist_x, dist_y):
        self.pos_x += dist_x
        self.pos_y += dist_y
    
    def accel(self, delta_vel_x, delta_vel_y):
        self.vel_x += delta_vel_x
        self.vel_y += delta_vel_y
    
    def update(self):
        self.move(self.vel_x, self.vel_y)
        self.accel(self.acc_x, self.acc_y)
        
    def simulate(self, center_x, center_y, gravity_module):
        self.accel((gravity_module * ((self.pos_x - center_x) / math.sqrt((self.pos_x - center_x) ** 2 + (self.pos_y - center_y) ** 2))) * -1, (gravity_module *((self.pos_y - center_y) / math.sqrt((self.pos_x - center_x) ** 2 + (self.pos_y - center_y) ** 2))) * -1)
        self.update()
        pygame.draw.circle(screen, self.color, (self.pos_x, self.pos_y), self.size)
    
projectile = Projectile(640, 180, 0.5, 0, 0, 0, 32, "red")

running = True
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE
    
    pygame.draw.circle(screen, "blue", (640, 360), 8)
    
    projectile.simulate(640, 360, 0.001)
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(240)  # limits FPS to 240

pygame.quit()