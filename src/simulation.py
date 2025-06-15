import pygame
import pygame.freetype
import math
import numpy as np

SCREEN_RES: np.ndarray = np.array([1280, 720], dtype=np.uint16)
ARROW_POLYGON_POINTS_ARRAY: np.ndarray = np.array([(0, 0), (-0.5, -0.5), (1, 0), (-0.5, 0.5)], dtype=np.double)

GRAVITATIONAL_CONSTANT: float = 6.6743 * (10 ** -11)
DENSITY: float = 5500 # density constant for mass and gravity force calculation, expressed in Kg/m³. Earth density is aprox. 5500 Kg/m³.
NULL_VECTOR: np.ndarray = np.array([0, 0], dtype=np.uint8)
UNIT_VECTOR: np.ndarray = np.array([1, 1], dtype=np.uint8)

# pygame setup
pygame.init()
clock = pygame.time.Clock()

def get_screen_pos(pos: np.ndarray, screen_center: np.ndarray, zoom: float):
    screen_pos: np.ndarray = np.array([pos[0], -pos[1]], dtype=np.double)
    screen_pos -= np.array([screen_center[0], -screen_center[1]])
    screen_pos *= zoom
    screen_pos += (SCREEN_RES / 2)
    screen_pos = screen_pos.astype(dtype=np.int16)
        
    return screen_pos
    
       
def draw_arrow(window, start_pos: np.ndarray, angle: float, modulus: float, color: tuple, screen_center: np.ndarray, zoom: float):
    end_pos: np.ndarray = start_pos + np.array([modulus * math.cos(math.radians(angle)), modulus * math.sin(math.radians(angle))], dtype=np.double)
    screen_pos_start: np.ndarray = get_screen_pos(start_pos, screen_center, zoom)
    screen_pos_end: np.ndarray = get_screen_pos(end_pos, screen_center, zoom)
    
    arrow_points: np.ndarray = ARROW_POLYGON_POINTS_ARRAY * zoom * 8
    rotation_matrix: np.ndarray = np.array([(math.cos(math.radians(angle)), -math.sin(math.radians(angle))), (math.sin(math.radians(angle)), math.cos(math.radians(angle)))], dtype=np.double)
    arrow_points @= rotation_matrix
    arrow_points += screen_pos_end
    
    pygame.draw.circle(window, color, screen_pos_start, int(2 * zoom))
    pygame.draw.line(window, color, screen_pos_start, screen_pos_end, int(2 * zoom))
    pygame.draw.polygon(window, color, arrow_points)

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
        
    def draw(self, window, screen_center: np.ndarray, zoom: float): # draws the projectile in screeen taking into account player movment and zoom
        screen_pos: np.ndarray = get_screen_pos(self.moment[0], screen_center, zoom)
    
        pygame.draw.circle(window, self.color, screen_pos, self.size * zoom)

# class GravityBody
class GravityBody:
    def __init__(self, pos: np.ndarray, diameter: float, color: tuple):
        self.pos: np.ndarray = pos # creates a 1x2 array that stores the position of the gravity body
        self.diameter: float = diameter # diameter of the gravity body, expressed in m
        self.color: tuple = color
        self.mass: float = (DENSITY * math.pi * (diameter ** 3)) / 6 # mass of the gravity body, expressed in Kg
        
    def draw(self, window, screen_center: np.ndarray, zoom: float): # draws the gravity body in screeen taking into account player movment and zoom
        screen_pos: np.ndarray = get_screen_pos(self.pos, screen_center, zoom)
    
        pygame.draw.circle(window, self.color, screen_pos, self.diameter/2 * zoom)
    
    def add_diameter(self, diameter:float):
        self.diameter += diameter
        self.mass: float = (DENSITY * math.pi * (self.diameter ** 3)) / 6
        
    def exerce_gravity(self, projectile: Projectile): # calculates the new moment exerced on the give projectile by this gravity body
        distance_from_center_of_mass: np.double = np.linalg.norm(projectile.moment[0] - self.pos)
        gravity_force: np.double = -(GRAVITATIONAL_CONSTANT * self.mass) / distance_from_center_of_mass ** 2 # signal of gravity_force is inverted to pull the projectille down instead of up
        
        cos_alpha: float = (projectile.moment[0, 0] - self.pos[0]) / distance_from_center_of_mass
        sen_alpha: float = (projectile.moment[0, 1] - self.pos[1]) / distance_from_center_of_mass
        
        projectile.simulate(np.array([gravity_force * cos_alpha, gravity_force * sen_alpha]))
    
    def check_collision(self, projectile: Projectile):
        distance_from_center_of_mass: np.double = np.linalg.norm(projectile.moment[0] - self.pos)
        return distance_from_center_of_mass <= self.diameter/2
       

# class Cannon
class Cannon:
    def __init__(self, height: int, gravity_body: GravityBody, angle: float, firing_speed_modulus: float):
        self.pos: np.ndarray = gravity_body.pos + np.array([0, height], dtype=np.int16) + np.array([0, gravity_body.diameter / 2], dtype=np.int16)
        self.gravity_body: GravityBody = gravity_body
        self.angle: float = angle
        self.firing_speed_modulus: float = firing_speed_modulus
        self.firing_speed = np.array([firing_speed_modulus * math.cos(math.radians(self.angle)), firing_speed_modulus * math.sin(math.radians(self.angle))])
        
    def draw(self, window, screen_center: np.ndarray, zoom: float): # draws the cannon in screeen taking into account player movment and zoom
        screen_pos_gravity_body: np.ndarray = get_screen_pos(self.gravity_body.pos, screen_center, zoom)
        screen_pos_cannon:np.ndarray = get_screen_pos(self.pos, screen_center, zoom)
        TAM: float = 16
        
        cannon_sprite: pygame.Rect = pygame.Rect(screen_pos_cannon[0] - TAM, screen_pos_cannon[1] - TAM, TAM * 2, TAM * 2)
        pygame.draw.line(window, (0, 255, 0), screen_pos_gravity_body, screen_pos_cannon, int(8 * zoom))
        pygame.draw.rect(window, (0, 255, 0), cannon_sprite.scale_by(zoom, zoom))
        draw_arrow(window, self.pos, self.angle, self.firing_speed_modulus * 50, (255, 0, 255), screen_center, zoom)
        
    def add_height(self, height: float):
        self.pos += np.array([0, height], dtype=np.int16)
    
    def add_angle(self, angle: float):
        self.angle += angle
        self.firing_speed = np.array([self.firing_speed_modulus * math.cos(math.radians(self.angle)), self.firing_speed_modulus * math.sin(math.radians(self.angle))])
        
    def add_speed_modulus(self, speed: float):
        self.firing_speed_modulus += speed
        self.firing_speed = np.array([self.firing_speed_modulus * math.cos(math.radians(self.angle)), self.firing_speed_modulus * math.sin(math.radians(self.angle))])
        
    def fire(self, projectile_size: float, projectile_color: tuple):
        projectile: Projectile = Projectile(np.array([self.pos[0], self.pos[1]]), np.array([self.firing_speed[0], self.firing_speed[1]]), projectile_size, projectile_color)
        return projectile

class Explosion:
    def __init__(self, pos: np.ndarray, size: float): # pos is the position of the projectile
        self.pos: np.ndarray = pos
        self.initial_size = size
        self.size = size
        self.iterations = 0
        self.max_iterations = 20
    
    def draw(self, window, screen_center: np.ndarray, zoom: float): 
        screen_pos: np.ndarray = get_screen_pos(self.pos, screen_center, zoom)
        progress = self.iterations / self.max_iterations

        if progress < 0.3: # yellow (255, 255, 0) to orange (255, 128, 0)
            g: int = 255 - int(255 * progress * 2)
        else: # orange to red (255, 0, 0)
            g: int = 128 - int(128 * (progress - 0.5) * 2)
        r: int = 255
        b: int = 0
        color: tuple = (r, g, b)

        pygame.draw.circle(window, color, screen_pos, self.size * zoom)
    
    def update(self):
        self.iterations += 1
        
        # explosion becomes bigger (first 10 iterations)
        if self.iterations <= 10:
            self.size = self.initial_size * 4 * (self.iterations / 10)
        else: # explosion becomes smaller
            self.size = self.initial_size * 4 * (self.max_iterations - self.iterations) / 10

        return self.iterations >= self.max_iterations

# class Screen
class Screen:
    def __init__(self, resolution: np.ndarray, font_size: int, background_color: tuple, planet: GravityBody, cannon: Cannon, projectiles, screen_center: np.ndarray, zoom: float): # font: pygame.freetype.Font
        self.resolution: np.ndarray = resolution
        self.backgound_color: tuple = background_color
        self.planet: GravityBody = planet
        self.cannon: Cannon = cannon
        self.projectiles = projectiles
        self.screen_center: np.ndarray = np.array(screen_center, dtype=np.double)
        self.zoom: float = zoom
        self.collision_count: int = 0
        self.window = pygame.display.set_mode(resolution)
        self.text = pygame.freetype.SysFont(pygame.freetype.get_default_font(), font_size)
        
    def controls(self, controlling, key, last_key_pressed):
        #key = pygame.key.get_pressed()
        #last_key_pressed: str
        match controlling:
            case "screen_pos":
                if key[pygame.K_UP] == True:
                    self.screen_center[1] += (1 / self.zoom)
                    last_key_pressed = "UP"
                elif key[pygame.K_RIGHT] == True:
                    self.screen_center[0] += (1 / self.zoom)
                    last_key_pressed = "RIGHT"
                elif key[pygame.K_DOWN] == True:
                    self.screen_center[1] -= (1 / self.zoom)
                    last_key_pressed = "DOWN"
                elif key[pygame.K_LEFT] == True:
                    self.screen_center[0] -= (1 / self.zoom)
                    last_key_pressed = "LEFT"
                elif key[pygame.K_KP_PLUS] == True:
                    self.zoom += 0.01
                    last_key_pressed = "+"
                elif key[pygame.K_KP_MINUS] == True:
                    self.zoom -= 0.01
                    last_key_pressed = "-"
                    
            case "planet":
                if key[pygame.K_KP_PLUS] == True:
                    self.planet.add_diameter(1.0)
                    last_key_pressed = "+"
                elif key[pygame.K_KP_MINUS] == True:
                    self.planet.add_diameter(-1.0)
                    last_key_pressed = "-"
        
            case "cannon":
                if key[pygame.K_UP] == True:
                    self.cannon.add_height(1)
                    last_key_pressed = "UP"
                elif key[pygame.K_DOWN] == True:
                    self.cannon.add_height(-1)
                    last_key_pressed = "DOWN"
                elif key[pygame.K_RIGHT] == True:
                    self.cannon.add_angle(0.1)
                    last_key_pressed = "RIGHT"
                elif key[pygame.K_LEFT] == True:
                    self.cannon.add_angle(-0.1)
                    last_key_pressed = "LEFT"
                elif key[pygame.K_KP_PLUS] == True:
                    self.cannon.add_speed_modulus(0.001)
                    last_key_pressed = "+"
                elif key[pygame.K_KP_MINUS] == True:
                    self.cannon.add_speed_modulus(-0.001)
                    last_key_pressed = "-"
                    
        return last_key_pressed
    
    def simulate(self):
        for projectile in projectiles:
            planet.exerce_gravity(projectile)
            if planet.check_collision(projectile):
                explosions.append(Explosion(projectile.moment[0], 16))
                projectiles.remove(projectile)
                self.collision_count += 1
        
    def draw(self, last_key_pressed: str, controlling: str):
        self.window.fill(self.backgound_color) # fill the screen with a color to wipe away anything from last frame
        
        for explosion in explosions:
            if explosion.update():
                explosions.remove(explosion)
            explosion.draw(self.window, self.screen_center, self.zoom)
        
        cannon.draw(self.window, self.screen_center, self.zoom)
        planet.draw(self.window, self.screen_center, self.zoom)
        for projectile in projectiles:
            planet.exerce_gravity(projectile)
            projectile.draw(self.window, self.screen_center, self.zoom)
        
        angle_display_txt = "Angle: {angle:.2f}°"
        velocity_display_txt = "Velocity: {speed: .2f} m/s"
        collision_display_txt = "Collisions: {count}"
        
        self.text.render_to(self.window, (0, 0), angle_display_txt.format(angle = self.cannon.angle), (255, 255, 255))
        self.text.render_to(self.window, (0, 32), velocity_display_txt.format(speed = self.cannon.firing_speed_modulus), (255, 255, 255))
        self.text.render_to(self.window, (0, 64), collision_display_txt.format(count = self.collision_count), (255, 255, 255))
    
        self.text.render_to(self.window, (0, 96), "Last key pressed: " + last_key_pressed, (255, 255, 255))
        self.text.render_to(self.window, (0, 128), "Controling: " + controlling, (255, 255, 255))
    
planet: GravityBody = GravityBody(np.array([0, 0]), 1024, (0, 0, 255))
cannon: Cannon = Cannon(64, planet, 0, 0.44)
projectiles = []
explosions = []

screen: Screen = Screen(SCREEN_RES, 32, (0, 0, 0), planet, cannon, projectiles, np.array([0, 0], dtype=np.double), 0.2)

last_key_pressed = "NONE"
controlling = "screen_pos"

running: bool = True

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
    
    # RENDER YOUR GAME HERE
    
    key = pygame.key.get_pressed()
    if key[pygame.K_KP1] == True:
        controlling = "screen_pos"
        last_key_pressed = "1"
    elif key[pygame.K_KP2] == True:
        controlling = "planet"
        last_key_pressed = "2"
    elif key[pygame.K_KP3] == True:
        controlling = "cannon"
        last_key_pressed = "3"
    else: 
        screen.controls(controlling, key, last_key_pressed)
    
    screen.simulate()
    screen.draw(last_key_pressed, controlling)
  
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(240)  # limits FPS to 240

pygame.quit()