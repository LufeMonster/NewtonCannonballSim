import pygame
import math

screen_res_x = 1280
screen_res_y = 720

GRAVITATIONAL_CONSTANT = 6.6743 * (10 ** -11)
DENSITY = 5500 # Density constant for mass and gravity force calculation. Expressed in Kg/m³. Earth density is aprox. 5500 Kg/m³.

# pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_res_x, screen_res_y))
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
        
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.pos_x, self.pos_y), self.size)

class GravityBody:
    def __init__(self, pos_x, pos_y, diameter, color):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.diameter = diameter
        self.color = color
        self.mass = (DENSITY * math.pi * (diameter ** 3)) / 6 # Mass of the planet. Expressed in Kg.
        
    def draw(self, color):
        pygame.draw.circle(screen, color, (self.pos_x, self.pos_y), self.diameter)
        
    def exerce_gravity(self, projectile: Projectile):
        delta_x = projectile.pos_x - self.pos_x
        delta_y = projectile.pos_y - self.pos_y
        
        distance_from_center_of_mass = math.sqrt(((delta_x) ** 2) + ((delta_y)**2))
        gravity_force = (GRAVITATIONAL_CONSTANT * self.mass) / distance_from_center_of_mass * -1
        
        projectile.accel(gravity_force * (delta_x / distance_from_center_of_mass), gravity_force * (delta_y / distance_from_center_of_mass))
        projectile.update()
    
projectile = Projectile(screen_res_x / 2, (screen_res_y / 2) - (screen_res_y / 4), 0.5, 0, 0, 0, 8, "red")

planet = GravityBody(screen_res_x / 2, screen_res_y / 2, 100, "blue")

print(GRAVITATIONAL_CONSTANT)

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
    
    planet.exerce_gravity(projectile)
    projectile.draw()
    planet.draw("blue")
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(240)  # limits FPS to 240

pygame.quit()