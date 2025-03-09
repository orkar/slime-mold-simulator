# Slime Mold Simulator

This simulator models the behavior of Physarum polycephalum (slime mold), demonstrating its remarkable ability to form efficient networks.

## Features

- **Thousands of Agent Particles**: Simulates individual slime mold particles that explore, deposit trails, and form networks
- **Chemical Trail System**: Agents deposit trails that diffuse and evaporate over time
- **Food Detection**: Agents can find food and strengthen paths between food sources
- **Network Formation**: The simulation demonstrates how slime mold forms efficient networks connecting food sources
- **Path Optimization**: Over time, the network optimizes to create more efficient paths
- **Interactive UI**: Adjust simulation parameters in real-time and place food manually

## Requirements

- Python 3.7+
- Flask
- NumPy

## Installation

1. Clone this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

1. Run the application:

```
python app.py
```

2. Open your browser and navigate to `http://127.0.0.1:5000`

3. Use the control buttons to start, stop, and reset the simulation

4. Click on the canvas to manually place food sources

5. Adjust simulation parameters using the sliders in the settings panel

## Configuration Parameters

### Agent Parameters
- **Number of Agents**: Controls the population of agent particles
- **Agent Speed**: Controls how fast agents move through the environment
- **Sensor Angle**: Angle between sensors used to detect chemical trails
- **Sensor Distance**: How far ahead agents can sense chemical trails
- **Turn Speed**: How quickly agents can change direction

### Trail Parameters
- **Trail Strength**: Intensity of the chemical trail deposited by agents
- **Evaporation Rate**: How quickly chemical trails fade away
- **Diffusion Rate**: How much trails spread to neighboring areas

### Food Parameters
- **Food Quantity**: Number of food sources in the environment
- **Food Spawn Rate**: Probability of new food appearing over time
- **Nucleus Size**: Size of the central nucleus (starting point)

## How It Works

The simulation is based on a simple model of how slime mold behaves:

1. **Exploration**: Agents start from a central nucleus and move outward, leaving chemical trails
2. **Trail Following**: Agents sense chemical trails ahead and tend to follow stronger trails
3. **Food Discovery**: When agents find food, they strengthen the trails between food and the nucleus
4. **Network Optimization**: Over time, frequent paths become stronger while unused paths fade away

This emergent behavior results in the formation of efficient networks connecting food sources, similar to how real slime mold optimizes for resource collection.

## License

This project is open source, available under the MIT License. 