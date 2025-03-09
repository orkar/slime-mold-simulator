from flask import Flask, render_template, jsonify, request
import json
import os
from src.api_routes import api

app = Flask(__name__, static_folder="static", template_folder="templates")

# Register the API blueprint
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    """Serve the main simulation page"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Return the default configuration parameters for the simulation"""
    config = {
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
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def set_config():
    """Update the simulation configuration parameters"""
    # This would actually modify the simulation in a real implementation
    data = request.get_json()
    return jsonify({"success": True, "config": data})

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True) 