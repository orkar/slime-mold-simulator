import numpy as np
import random
import math

class Agent:
    """
    Represents an individual slime mold agent particle
    """
    def __init__(self, x, y, angle, speed, world):
        self.x = x
        self.y = y
        self.angle = angle  # Direction in radians
        self.speed = speed
        self.world = world
        self.has_food = False
        self.food_timer = 0
        
    def sense(self, sensor_angle, sensor_distance):
        """Sense chemical trails in different directions"""
        # Create three sensors: left, center, and right
        left_angle = self.angle - math.radians(sensor_angle)
        right_angle = self.angle + math.radians(sensor_angle)
        
        # Get sensor positions
        left_x = int(self.x + sensor_distance * math.cos(left_angle))
        left_y = int(self.y + sensor_distance * math.sin(left_angle))
        center_x = int(self.x + sensor_distance * math.cos(self.angle))
        center_y = int(self.y + sensor_distance * math.sin(self.angle))
        right_x = int(self.x + sensor_distance * math.cos(right_angle))
        right_y = int(self.y + sensor_distance * math.sin(right_angle))
        
        # Get trail values at sensor positions (with boundary checking)
        left_value = self.world.get_trail(left_x, left_y)
        center_value = self.world.get_trail(center_x, center_y)
        right_value = self.world.get_trail(right_x, right_y)
        
        return left_value, center_value, right_value
    
    def move(self, turn_speed, sensor_angle, sensor_distance):
        """Move the agent based on sensors and update the world"""
        # Sense chemicals around
        left, center, right = self.sense(sensor_angle, sensor_distance)
        
        # Determine turning behavior
        if center > left and center > right:
            # Continue straight
            pass
        elif left > right:
            # Turn left
            self.angle -= math.radians(turn_speed)
        elif right > left:
            # Turn right
            self.angle += math.radians(turn_speed)
        else:
            # Random direction if equal
            self.angle += math.radians(turn_speed * random.uniform(-1, 1))
        
        # Add some randomness to movement
        self.angle += math.radians(random.uniform(-15, 15))
        
        # Calculate new position
        new_x = self.x + self.speed * math.cos(self.angle)
        new_y = self.y + self.speed * math.sin(self.angle)
        
        # Check if new position is valid (within bounds)
        if self.world.is_valid_position(new_x, new_y):
            # Check for food at the new position
            if self.world.has_food(int(new_x), int(new_y)):
                self.has_food = True
                self.food_timer = 100  # Will deposit stronger trail for this many steps
                
            # Update position
            self.x = new_x
            self.y = new_y
            
            # Deposit trail
            trail_strength = self.world.config['trail_strength']
            if self.has_food and self.food_timer > 0:
                # Deposit stronger trail when returning with food
                self.world.deposit_trail(int(self.x), int(self.y), trail_strength * 5)
                self.food_timer -= 1
                if self.food_timer <= 0:
                    self.has_food = False
            else:
                # Normal trail deposition
                self.world.deposit_trail(int(self.x), int(self.y), trail_strength)
        else:
            # Hit boundary, change to random direction
            self.angle = random.uniform(0, 2 * math.pi)


class World:
    """
    Represents the environment for the slime mold simulation
    """
    def __init__(self, width, height, config):
        self.width = width
        self.height = height
        self.config = config
        
        # Initialize grid for chemical trails
        self.trail_map = np.zeros((height, width), dtype=np.float32)
        
        # Initialize grid for food
        self.food_map = np.zeros((height, width), dtype=np.bool_)
        
        # Initialize agents
        self.agents = []
        self.initialize_agents()
        
        # Initialize food
        self.initialize_food()
        
        # Create nucleus in the center
        self.nucleus_x = width // 2
        self.nucleus_y = height // 2
        self.nucleus_size = config['nucleus_size']
        
    def initialize_agents(self):
        """Create initial agents at the nucleus"""
        num_agents = self.config['num_agents']
        agent_speed = self.config['agent_speed']
        
        for _ in range(num_agents):
            # Start at the nucleus with random directions
            angle = random.uniform(0, 2 * math.pi)
            agent = Agent(self.width // 2, self.height // 2, angle, agent_speed, self)
            self.agents.append(agent)
    
    def initialize_food(self):
        """Place random food sources in the environment"""
        food_quantity = self.config['food_quantity']
        
        for _ in range(food_quantity):
            # Avoid placing food too close to the nucleus
            while True:
                x = random.randint(20, self.width - 20)
                y = random.randint(20, self.height - 20)
                
                # Check if it's not too close to nucleus
                distance_to_nucleus = math.sqrt((x - self.nucleus_x)**2 + (y - self.nucleus_y)**2)
                if distance_to_nucleus > 50:
                    self.food_map[y, x] = True
                    break
    
    def is_valid_position(self, x, y):
        """Check if a position is within bounds"""
        x_int, y_int = int(x), int(y)
        return 0 <= x_int < self.width and 0 <= y_int < self.height
    
    def has_food(self, x, y):
        """Check if there is food at the given position"""
        if not self.is_valid_position(x, y):
            return False
        return self.food_map[y, x]
    
    def get_trail(self, x, y):
        """Get the trail value at a position (with bounds checking)"""
        if not self.is_valid_position(x, y):
            return 0
        return self.trail_map[y, x]
    
    def deposit_trail(self, x, y, amount):
        """Add chemical trail at the given position"""
        if self.is_valid_position(x, y):
            self.trail_map[y, x] += amount
            
    def diffuse_trails(self):
        """Diffuse chemical trails to neighboring cells"""
        diffusion_rate = self.config['trail_diffusion_rate']
        
        # Create a kernel for diffusion
        kernel = np.array([[0.05, 0.2, 0.05], 
                           [0.2, 0, 0.2], 
                           [0.05, 0.2, 0.05]])
        
        # Apply diffusion
        diffused = np.zeros_like(self.trail_map)
        
        # Manual convolution (for simplicity - could be optimized)
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Calculate how much to diffuse to neighbors
                amount_to_diffuse = self.trail_map[y, x] * diffusion_rate
                
                # Keep the rest in the current cell
                diffused[y, x] += self.trail_map[y, x] - amount_to_diffuse
                
                # Distribute to neighbors according to kernel weights
                for ky in range(3):
                    for kx in range(3):
                        if kernel[ky, kx] > 0:
                            ny, nx = y + ky - 1, x + kx - 1
                            diffused[ny, nx] += amount_to_diffuse * kernel[ky, kx]
        
        self.trail_map = diffused
    
    def evaporate_trails(self):
        """Reduce chemical trail strength over time"""
        evaporation_rate = self.config['trail_evaporation_rate']
        self.trail_map *= (1 - evaporation_rate)
    
    def update(self):
        """Update the entire simulation for one time step"""
        # Update each agent
        for agent in self.agents:
            agent.move(
                self.config['turn_speed'],
                self.config['sensor_angle'],
                self.config['sensor_distance']
            )
        
        # Diffuse and evaporate trails
        self.diffuse_trails()
        self.evaporate_trails()
        
        # Possibly spawn new food
        if random.random() < self.config['food_spawn_rate']:
            x = random.randint(10, self.width - 10)
            y = random.randint(10, self.height - 10)
            
            # Don't spawn on the nucleus
            distance_to_nucleus = math.sqrt((x - self.nucleus_x)**2 + (y - self.nucleus_y)**2)
            if distance_to_nucleus > 50:
                self.food_map[y, x] = True
    
    def get_state(self):
        """Return the current state of the world for visualization"""
        return {
            'trail_map': self.trail_map.tolist(),
            'food_map': self.food_map.tolist(),
            'nucleus': {
                'x': self.nucleus_x,
                'y': self.nucleus_y,
                'size': self.nucleus_size
            }
        } 