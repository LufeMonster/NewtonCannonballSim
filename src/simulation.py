import pygame
import math
import numpy as np

SCREEN_RES: np.ndarray = np.array([1280, 720], dtype=np.uint16)

GRAVITATIONAL_CONSTANT: float = 6.6743 * (10 ** -11)
DENSITY: float = 5500 # Density constant for mass and gravity force calculation. Expressed in Kg/m³. Earth density is aprox. 5500 Kg/m³.
NULL_VECTOR: np.ndarray = np.array([0, 0], dtype=np.uint8)
UNIT_VECTOR: np.ndarray = np.array([1, 1], dtype=np.uint8)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_RES[0], SCREEN_RES[1]))
clock = pygame.time.Clock()

# Class Projectile
class Projectile:
    def __init__(self, pos: np.ndarray, vel: np.ndarray, size: float, color: tuple):
        self.moment: np.ndarray = np.array([pos, vel], dtype=np.double)
        self.size: float = size
        self.color: tuple = color
    
    def move(self, dist: np.ndarray):
        self.moment += np.array([dist, NULL_VECTOR])
    
    def accel(self, delta_v: np.ndarray):
        self.moment += np.array([NULL_VECTOR, delta_v])
        
    def update(self):
        self.moment += np.array([self.moment[1], NULL_VECTOR])
        
    def simulate(self, delta_a: np.ndarray):
        self.moment += np.array([self.moment[1], delta_a])
        
    def draw(self, screen_center: np.ndarray, zoom: float):
        screen_pos: np.ndarray = np.array([self.moment[0, 0], - self.moment[0, 1]], dtype=np.double)
        screen_pos -= np.array([screen_center[0], -screen_center[1]])
        screen_pos *= zoom
        screen_pos += (SCREEN_RES / 2)
        screen_pos = screen_pos.astype(dtype=np.int64)
    
        if NULL_VECTOR[0] <= screen_pos[0] <= SCREEN_RES[0] and NULL_VECTOR[1] <= screen_pos[1] <= SCREEN_RES[1]:
            pygame.draw.circle(screen, self.color, screen_pos, self.size * zoom)

class GravityBody:
    def __init__(self, pos: np.ndarray, diameter: float, color: tuple):
        self.pos: np.ndarray = pos
        self.diameter: float = diameter
        self.color: tuple = color
        self.mass: float = (DENSITY * math.pi * (diameter ** 3)) / 6 # Mass of the planet. Expressed in Kg.
        
    def draw(self, screen_center: np.ndarray, zoom: float):
        screen_pos: np.ndarray = np.array([self.pos[0], -self.pos[1]], dtype=np.double)
        screen_pos -= np.array([screen_center[0], -screen_center[1]])
        screen_pos *= zoom
        screen_pos += (SCREEN_RES / 2)
        screen_pos = screen_pos.astype(dtype=np.int64)
    
        if NULL_VECTOR[0] <= screen_pos[0] <= SCREEN_RES[0] and NULL_VECTOR[1] <= screen_pos[1] <= SCREEN_RES[1]:
            pygame.draw.circle(screen, self.color, screen_pos, self.diameter * zoom)
        
    def exerce_gravity(self, projectile: Projectile):
        distance_from_center_of_mass = np.linalg.norm(projectile.moment[0] - self.pos)
        gravity_force = -(GRAVITATIONAL_CONSTANT * self.mass) / distance_from_center_of_mass
        
        cos_alpha = (projectile.moment[0, 0] - self.pos[0]) / distance_from_center_of_mass
        sen_alpha = (projectile.moment[0, 1] - self.pos[1]) / distance_from_center_of_mass
        
        projectile.simulate(np.array([gravity_force * cos_alpha, gravity_force * sen_alpha]))
        
projectile: Projectile = Projectile(np.array([0, 180]), np.array([0.5, 0]), 8, (255, 0, 0))

planet: GravityBody = GravityBody(np.array([0, 0]), 100, (0, 0, 255))

screen_center: np.ndarray = np.array([0, 0], dtype=np.double)
zoom: float = 1

running: bool = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    key = pygame.key.get_pressed()
    if key[pygame.K_UP] == True:
        screen_center[1] += (1 / zoom)
    elif key[pygame.K_RIGHT] == True:
        screen_center[0] += (1 / zoom)
    elif key[pygame.K_DOWN] == True:
        screen_center[1] -= (1 / zoom)
    elif key[pygame.K_LEFT] == True:
        screen_center[0] -= (1 / zoom)
    elif key[pygame.K_KP_PLUS] == True:
        zoom += 0.01
    elif key[pygame.K_KP_MINUS] == True:
        zoom -= 0.01
        
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE
    
    planet.draw(screen_center, zoom)
    planet.exerce_gravity(projectile)

    projectile.draw(screen_center, zoom)
    # print("pos_x:", projectile.pos_x, "pos_y:", projectile.pos_y)
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(240)  # limits FPS to 240

pygame.quit()