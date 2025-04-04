import pygame
import pygame.freetype
import math
import numpy as np

SCREEN_RES: np.ndarray = np.array([1280, 720], dtype=np.uint16)

GRAVITATIONAL_CONSTANT: float = 6.6743 * (10 ** -11)
DENSITY: float = 5500 # density constant for mass and gravity force calculation, expressed in Kg/m³. Earth density is aprox. 5500 Kg/m³.
NULL_VECTOR: np.ndarray = np.array([0, 0], dtype=np.uint8)
UNIT_VECTOR: np.ndarray = np.array([1, 1], dtype=np.uint8)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_RES[0], SCREEN_RES[1]))
SIM_FONT = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 32)
clock = pygame.time.Clock()

# class Projectile
class Projectile:
    def __init__(self, pos: np.ndarray, vel: np.ndarray, size: float, color: tuple):
        self.moment: np.ndarray = np.array([pos, vel], dtype=np.double) # creates a 2x2 array that stores the position and velocity of the projectile
        self.size: float = size # size of the projectile, expressed in m
        self.color: tuple = color # color in (r, g, b) format
    
    def move(self, dist: np.ndarray):
        self.moment += np.array([dist, NULL_VECTOR])
    
    def accel(self, delta_v: np.ndarray):
        self.moment += np.array([NULL_VECTOR, delta_v])
        
    def update(self): # updates position based on current velocity without accelerating
        self.moment += np.array([self.moment[1], NULL_VECTOR])
        
    def simulate(self, delta_a: np.ndarray): # accelerate and update velocity at the same time, useful when exercing gravity calculations
        self.moment += np.array([self.moment[1], delta_a])
        
    def get_screen_pos(self,screen_center: np.ndarray, zoom: float):
        screen_pos: np.ndarray = np.array([self.moment[0, 0], - self.moment[0, 1]], dtype=np.double)
        screen_pos -= np.array([screen_center[0], -screen_center[1]])
        screen_pos *= zoom
        screen_pos += (SCREEN_RES / 2)
        screen_pos = screen_pos.astype(dtype=np.int16)
        
        return screen_pos
        
    def draw(self, screen_center: np.ndarray, zoom: float): # draws the projectile in screeen taking into account player movment and zoom
        screen_pos: np.ndarray = self.get_screen_pos(screen_center, zoom)
    
        if NULL_VECTOR[0] <= screen_pos[0] <= SCREEN_RES[0] and NULL_VECTOR[1] <= screen_pos[1] <= SCREEN_RES[1]: # cheks if the projectile is in the boundaries of the screen before drawing it
            pygame.draw.circle(screen, self.color, screen_pos, self.size * zoom)

# class GravityBody
class GravityBody:
    def __init__(self, pos: np.ndarray, diameter: float, color: tuple):
        self.pos: np.ndarray = pos # creates a 1x2 array that stores the position of the gravity body
        self.diameter: float = diameter # diameter of the gravity body, expressed in m
        self.color: tuple = color
        self.mass: float = (DENSITY * math.pi * (diameter ** 3)) / 6 # mass of the gravity body, expressed in Kg
        
    def get_screen_pos(self,screen_center: np.ndarray, zoom: float):
        screen_pos: np.ndarray = np.array([self.pos[0], -self.pos[1]], dtype=np.double)
        screen_pos -= np.array([screen_center[0], -screen_center[1]])
        screen_pos *= zoom
        screen_pos += (SCREEN_RES / 2)
        screen_pos = screen_pos.astype(dtype=np.int16)
        
        return screen_pos
        
    def draw(self, screen_center: np.ndarray, zoom: float): # draws the gravity body in screeen taking into account player movment and zoom
        screen_pos: np.ndarray = self.get_screen_pos(screen_center, zoom)
        
        if NULL_VECTOR[0] <= screen_pos[0] <= SCREEN_RES[0] and NULL_VECTOR[1] <= screen_pos[1] <= SCREEN_RES[1]: # cheks if the gravity body is in the boundaries of the screen before drawing it
            pygame.draw.circle(screen, self.color, screen_pos, self.diameter * zoom)
        
    def exerce_gravity(self, projectile: Projectile): # calculates the new moment exerced on the give projectile by this gravity body
        distance_from_center_of_mass: np.double = np.linalg.norm(projectile.moment[0] - self.pos)
        gravity_force: np.double = -(GRAVITATIONAL_CONSTANT * self.mass) / distance_from_center_of_mass # signal of gravity_force is inverted to pull the projectille down instead of up
        
        cos_alpha: float = (projectile.moment[0, 0] - self.pos[0]) / distance_from_center_of_mass
        sen_alpha: float = (projectile.moment[0, 1] - self.pos[1]) / distance_from_center_of_mass
        
        projectile.simulate(np.array([gravity_force * cos_alpha, gravity_force * sen_alpha]))

# class Cannon
class Cannon:
    def __init__(self, pos: np.ndarray, gravity_body: GravityBody, angle: float, firing_speed_modulus: float):
        self.pos: np.ndarray = pos + gravity_body.pos
        self.gravity_body: GravityBody = gravity_body
        self.angle: float = angle
        self.firing_speed_modulus: float = firing_speed_modulus
        self.firing_speed = np.array([firing_speed_modulus * math.cos(math.radians(self.angle)), firing_speed_modulus * math.sin(math.radians(self.angle))])
        
    def get_screen_pos(self,screen_center: np.ndarray, zoom: float):
        screen_pos: np.ndarray = np.array([self.pos[0], -self.pos[1]], dtype=np.double)
        screen_pos -= np.array([screen_center[0], -screen_center[1]])
        screen_pos *= zoom
        screen_pos += (SCREEN_RES / 2)
        screen_pos = screen_pos.astype(dtype=np.int16)
        
        return screen_pos
        
    def draw(self, screen_center: np.ndarray, zoom: float): # draws the gravity body in screeen taking into account player movment and zoom
        screen_pos_gravity_body: np.ndarray = self.gravity_body.get_screen_pos(screen_center, zoom)
        screen_pos_cannon:np.ndarray = self.get_screen_pos(screen_center, zoom)
        TAM: float = 16
        
        cannon_sprite: pygame.Rect = pygame.Rect(screen_pos_cannon[0] - TAM, screen_pos_cannon[1] - TAM, TAM * 2, TAM * 2)
        pygame.draw.line(screen, (0, 255, 0), screen_pos_gravity_body, screen_pos_cannon, int(8 * zoom))
        pygame.draw.rect(screen, (0, 255, 0), cannon_sprite.scale_by(zoom))
        
    def fire(self, projectile_size: float, projectile_color: tuple):
        self.firing_speed = np.array([self.firing_speed_modulus * math.cos(math.radians(self.angle)), self.firing_speed_modulus * math.sin(math.radians(self.angle))])
        projectile: Projectile = Projectile(np.array([self.pos[0], self.pos[1]]), np.array([self.firing_speed[0], self.firing_speed[1]]), projectile_size, projectile_color)
        return projectile

planet: GravityBody = GravityBody(np.array([0, 0]), 100, (0, 0, 255))
cannon: Cannon = Cannon(np.array([0, 180]), planet, 0, 0.44)
projectiles = []

screen_center: np.ndarray = np.array([0, 0], dtype=np.double)
zoom: float = 1

running: bool = True

last_key_pressed = "NONE"

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                projectiles.append(cannon.fire(8, (255, 0, 0)))
                last_key_pressed = "SPACE"
    
    
    key = pygame.key.get_pressed()
    if key[pygame.K_w] == True:
        screen_center[1] += (1 / zoom)
        last_key_pressed = "w"
    elif key[pygame.K_d] == True:
        screen_center[0] += (1 / zoom)
        last_key_pressed = "d"
    elif key[pygame.K_s] == True:
        screen_center[1] -= (1 / zoom)
        last_key_pressed = "s"
    elif key[pygame.K_a] == True:
        screen_center[0] -= (1 / zoom)
        last_key_pressed = "a"
    elif key[pygame.K_KP_PLUS] == True:
        zoom += 0.01
        last_key_pressed = "+"
    elif key[pygame.K_KP_MINUS] == True:
        zoom -= 0.01
        last_key_pressed = "-"
        
    elif key[pygame.K_UP] == True:
        cannon.angle += 0.1
        last_key_pressed = "UP"
    elif key[pygame.K_DOWN] == True:
        cannon.angle -= 0.1
        last_key_pressed = "DOWN"
    elif key[pygame.K_RIGHT] == True:
        cannon.firing_speed_modulus += 0.001
        last_key_pressed = "RIGHT"
    elif key[pygame.K_LEFT] == True:
        cannon.firing_speed_modulus -= 0.001
        last_key_pressed = "LEFT"
        
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE
    
    cannon.draw(screen_center, zoom)
    planet.draw(screen_center, zoom)
    
    for projectile in projectiles:
        planet.exerce_gravity(projectile)
        projectile.draw(screen_center, zoom)
        
    angle_display_txt = "Angle: {angle:.2f}°"
    velocity_display_txt = "Velocity: {speed: .2f} m/s"
    
    SIM_FONT.render_to(screen, (0, 0), angle_display_txt.format(angle = cannon.angle), (255, 255, 255))
    SIM_FONT.render_to(screen, (0, 32), velocity_display_txt.format(speed = cannon.firing_speed_modulus), (255, 255, 255))
    
    SIM_FONT.render_to(screen, (0, 64), "Last key pressed: " + last_key_pressed, (255, 255, 255))
    
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(240)  # limits FPS to 240

pygame.quit()