import threading
import time
import json
from .slime_mold import World

class SimulationController:
    """
    Controller for running the slime mold simulation and providing data to the web interface
    """
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.simulation_active = False
        self.simulation_thread = None
        self.fps = 30
        self.default_config = {
            'num_agents': 5000,
            'agent_speed': 1.0,
            'sensor_angle': 45,
            'sensor_distance': 9,
            'turn_speed': 0.5,
            'trail_strength': 5,
            'trail_evaporation_rate': 0.02,
            'trail_diffusion_rate': 0.1,
            'food_quantity': 15,
            'food_spawn_rate': 0,
            'nucleus_size': 25
        }
        self.config = self.default_config.copy()
        self.world = World(width, height, self.config)
        self.simulation_data = None
        self.frame_count = 0
        self.last_update_time = time.time()
        
    def start_simulation(self):
        """Start the simulation in a separate thread"""
        if not self.simulation_active:
            self.simulation_active = True
            self.simulation_thread = threading.Thread(target=self._simulation_loop)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
            return True
        return False
    
    def stop_simulation(self):
        """Stop the running simulation"""
        if self.simulation_active:
            self.simulation_active = False
            if self.simulation_thread:
                self.simulation_thread.join(timeout=1.0)
            return True
        return False
    
    def _simulation_loop(self):
        """Main loop for running the simulation"""
        while self.simulation_active:
            start_time = time.time()
            
            # Update the simulation
            self.world.update()
            
            # Get current simulation state
            self.simulation_data = self.world.get_state()
            
            # Calculate FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_update_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_update_time = current_time
            
            # Sleep to maintain stable frame rate (target ~30 FPS)
            elapsed = time.time() - start_time
            sleep_time = max(0, 1.0/30.0 - elapsed)
            time.sleep(sleep_time)
    
    def get_simulation_data(self):
        """Get the current state of the simulation"""
        if self.simulation_data:
            return {
                'world_data': self.simulation_data,
                'fps': self.fps,
                'is_running': self.simulation_active
            }
        return {
            'error': 'Simulation not running',
            'is_running': self.simulation_active
        }
    
    def update_config(self, new_config):
        """Update the simulation configuration"""
        # Update only the provided parameters
        for key, value in new_config.items():
            if key in self.config:
                self.config[key] = value
                
        # If simulation is running, need to restart with new settings
        was_running = self.simulation_active
        if was_running:
            self.stop_simulation()
            
        # Create a new world with updated config
        self.world = World(self.width, self.height, self.config)
        
        # Restart if it was running
        if was_running:
            self.start_simulation()
            
        return self.config
    
    def add_food(self, x, y):
        """Manually add food at the specified location"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.world.food_map[y, x] = True
            return True
        return False
    
    def reset_simulation(self):
        """Reset the simulation to its initial state"""
        was_running = self.simulation_active
        if was_running:
            self.stop_simulation()
            
        # Create a new world
        self.world = World(self.width, self.height, self.config)
        
        if was_running:
            self.start_simulation()
            
        return True 