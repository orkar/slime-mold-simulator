from flask import Blueprint, jsonify, request
from src.core.simulation import SimulationController

# Create a simulation controller with default settings
simulation = SimulationController(width=800, height=600)

# Create a blueprint for the API
api = Blueprint('api', __name__)

@api.route('/start', methods=['POST'])
def start_simulation():
    """Start the simulation"""
    success = simulation.start_simulation()
    return jsonify({'success': success})

@api.route('/stop', methods=['POST'])
def stop_simulation():
    """Stop the simulation"""
    success = simulation.stop_simulation()
    return jsonify({'success': success})

@api.route('/reset', methods=['POST'])
def reset_simulation():
    """Reset the simulation to initial state"""
    success = simulation.reset_simulation()
    return jsonify({'success': success})

@api.route('/data', methods=['GET'])
def get_simulation_data():
    """Get the current simulation state data"""
    data = simulation.get_simulation_data()
    return jsonify(data)

@api.route('/config', methods=['GET'])
def get_config():
    """Get the current simulation configuration"""
    return jsonify(simulation.config)

@api.route('/config', methods=['POST'])
def update_config():
    """Update the simulation configuration"""
    new_config = request.get_json()
    updated_config = simulation.update_config(new_config)
    return jsonify({'success': True, 'config': updated_config})

@api.route('/add_food', methods=['POST'])
def add_food():
    """Add food at a specified location"""
    data = request.get_json()
    x = data.get('x')
    y = data.get('y')
    
    if x is None or y is None:
        return jsonify({'success': False, 'error': 'Missing coordinates'}), 400
    
    success = simulation.add_food(int(x), int(y))
    return jsonify({'success': success})

@api.route('/status', methods=['GET'])
def get_status():
    """Get the current status of the simulation"""
    return jsonify({
        'is_running': simulation.simulation_active,
        'fps': simulation.fps
    }) 