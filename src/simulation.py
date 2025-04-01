import pygame
import math

SCREEN_RES_X = 1280
SCREEN_RES_Y = 720

GRAVITATIONAL_CONSTANT = 6.6743 * (10 ** -11)
DENSITY = 5500 # Density constant for mass and gravity force calculation. Expressed in Kg/m³. Earth density is aprox. 5500 Kg/m³.

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_RES_X, SCREEN_RES_Y))
clock = pygame.time.Clock()

# Class Projectile
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
        
    def draw(self, screen_center_x, screen_center_y, zoom):
        screen_pos_x = self.pos_x * zoom - screen_center_x + (SCREEN_RES_X / 2)
        screen_pos_y = - self.pos_y * zoom + screen_center_y + (SCREEN_RES_Y / 2)
        
        if 0 <= screen_pos_x <= SCREEN_RES_X and 0 <= screen_pos_y <= SCREEN_RES_Y:
            pygame.draw.circle(screen, self.color, (screen_pos_x, screen_pos_y), self.size * zoom)

class GravityBody:
    def __init__(self, pos_x, pos_y, diameter, color):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.diameter = diameter
        self.color = color
        self.mass = (DENSITY * math.pi * (diameter ** 3)) / 6 # Mass of the planet. Expressed in Kg.
        
    def draw(self, screen_center_x, screen_center_y, zoom):
        screen_pos_x = self.pos_x * zoom - screen_center_x + (SCREEN_RES_X / 2)
        screen_pos_y = - self.pos_y  * zoom + screen_center_y + (SCREEN_RES_Y / 2)
        if 0 <= screen_pos_x <= SCREEN_RES_X and 0 <= screen_pos_y <= SCREEN_RES_Y:
            pygame.draw.circle(screen, self.color, (screen_pos_x, screen_pos_y), self.diameter * zoom)
        
    def exerce_gravity(self, projectile: Projectile):
        delta_x = projectile.pos_x - self.pos_x
        delta_y = projectile.pos_y - self.pos_y
        
        distance_from_center_of_mass = math.sqrt(((delta_x) ** 2) + ((delta_y)**2))
        gravity_force = -(GRAVITATIONAL_CONSTANT * self.mass) / distance_from_center_of_mass
        
        projectile.accel(gravity_force * (delta_x / distance_from_center_of_mass), gravity_force * (delta_y / distance_from_center_of_mass))
        projectile.update()
    
projectile = Projectile(0, 180, 0.5, 0, 0, 0, 8, "red")

planet = GravityBody(0, 0, 100, "blue")

screen_center_x = 0
screen_center_y = 0
zoom = 1

running = True
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    key = pygame.key.get_pressed()
    if key[pygame.K_UP] == True:
        screen_center_y += 1
    elif key[pygame.K_RIGHT] == True:
        screen_center_x += 1
    elif key[pygame.K_DOWN] == True:
        screen_center_y -= 1
    elif key[pygame.K_LEFT] == True:
        screen_center_x -= 1
    elif key[pygame.K_KP_PLUS] == True:
        zoom += 0.01
    elif key[pygame.K_KP_MINUS] == True:
        zoom -= 0.01
        
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE
    
    planet.draw(screen_center_x, screen_center_y, zoom)
    planet.exerce_gravity(projectile)

    projectile.draw(screen_center_x, screen_center_y, zoom)
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(240)  # limits FPS to 240

pygame.quit()