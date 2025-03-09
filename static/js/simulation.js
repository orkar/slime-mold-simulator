document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const resetBtn = document.getElementById('reset-btn');
    const applyBtn = document.getElementById('apply-btn');
    const fpsCounter = document.getElementById('fps-counter');
    const statsDisplay = document.getElementById('stats');

    // Simulation state
    let isRunning = false;
    let simulationData = null;
    let foodCount = 0;
    let networkLength = 0;
    
    // Color settings for visualization
    const colors = {
        background: '#000000',
        trailMin: 'rgba(50, 200, 50, 0.4)',
        trailMax: 'rgba(240, 255, 0, 0.9)',
        food: 'rgba(255, 255, 255, 0.9)',
        nucleus: 'rgba(255, 255, 0, 0.9)'
    };
    
    // Configuration
    let config = {
        num_agents: 5000,
        agent_speed: 1.0,
        sensor_angle: 45,
        sensor_distance: 9,
        turn_speed: 0.5,
        trail_strength: 5,
        trail_evaporation_rate: 0.02,
        trail_diffusion_rate: 0.1,
        food_quantity: 15,
        food_spawn_rate: 0,
        nucleus_size: 25
    };
    
    // Setup slider event listeners
    setupSliders();
    
    // Initialize canvas size
    initCanvas();
    
    // Event listeners
    startBtn.addEventListener('click', startSimulation);
    stopBtn.addEventListener('click', stopSimulation);
    resetBtn.addEventListener('click', resetSimulation);
    applyBtn.addEventListener('click', applySettings);
    canvas.addEventListener('click', handleCanvasClick);
    
    // Main animation loop
    let animationId = null;
    
    // Fetch initial configuration
    fetchConfig();
    
    // Functions
    
    function fetchConfig() {
        fetch('/api/config')
            .then(response => response.json())
            .then(data => {
                config = data;
                updateSliderValues();
                resetSimulation();
            })
            .catch(error => console.error('Error fetching config:', error));
    }
    
    function startSimulation() {
        if (isRunning) return;
        
        fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    isRunning = true;
                    startAnimationLoop();
                }
            })
            .catch(error => console.error('Error starting simulation:', error));
    }
    
    function stopSimulation() {
        if (!isRunning) return;
        
        fetch('/api/stop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    isRunning = false;
                    if (animationId) {
                        cancelAnimationFrame(animationId);
                        animationId = null;
                    }
                }
            })
            .catch(error => console.error('Error stopping simulation:', error));
    }
    
    function resetSimulation() {
        fetch('/api/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fetchSimulationData();
                }
            })
            .catch(error => console.error('Error resetting simulation:', error));
    }
    
    function applySettings() {
        const newConfig = {
            num_agents: parseInt(document.getElementById('num-agents').value),
            agent_speed: parseFloat(document.getElementById('agent-speed').value),
            sensor_angle: parseInt(document.getElementById('sensor-angle').value),
            sensor_distance: parseInt(document.getElementById('sensor-distance').value),
            turn_speed: parseFloat(document.getElementById('turn-speed').value),
            trail_strength: parseInt(document.getElementById('trail-strength').value),
            trail_evaporation_rate: parseFloat(document.getElementById('trail-evaporation').value),
            trail_diffusion_rate: parseFloat(document.getElementById('trail-diffusion').value),
            food_quantity: parseInt(document.getElementById('food-quantity').value),
            food_spawn_rate: parseFloat(document.getElementById('food-spawn-rate').value),
            nucleus_size: parseInt(document.getElementById('nucleus-size').value)
        };
        
        fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newConfig)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    config = data.config;
                    resetSimulation();
                }
            })
            .catch(error => console.error('Error applying settings:', error));
    }
    
    function fetchSimulationData() {
        fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                if (data.world_data) {
                    simulationData = data.world_data;
                    drawSimulation();
                    
                    // Update FPS
                    fpsCounter.textContent = `FPS: ${data.fps || 0}`;
                    
                    // Update run status
                    if (data.is_running !== isRunning) {
                        isRunning = data.is_running;
                        if (isRunning && !animationId) {
                            startAnimationLoop();
                        } else if (!isRunning && animationId) {
                            cancelAnimationFrame(animationId);
                            animationId = null;
                        }
                    }
                }
            })
            .catch(error => console.error('Error fetching simulation data:', error));
    }
    
    function startAnimationLoop() {
        const loop = () => {
            fetchSimulationData();
            if (isRunning) {
                animationId = requestAnimationFrame(loop);
            }
        };
        
        animationId = requestAnimationFrame(loop);
    }
    
    function handleCanvasClick(event) {
        const rect = canvas.getBoundingClientRect();
        const x = Math.floor((event.clientX - rect.left) * (canvas.width / rect.width));
        const y = Math.floor((event.clientY - rect.top) * (canvas.height / rect.height));
        
        fetch('/api/add_food', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ x, y })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Visual feedback for food placement
                    ctx.fillStyle = colors.food;
                    ctx.beginPath();
                    ctx.arc(x, y, 5, 0, Math.PI * 2);
                    ctx.fill();
                }
            })
            .catch(error => console.error('Error adding food:', error));
    }
    
    function drawSimulation() {
        if (!simulationData) return;
        
        // Clear canvas
        ctx.fillStyle = colors.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Get data
        const { trail_map, food_map, nucleus } = simulationData;
        
        // Find the maximum trail value for normalization
        let maxTrail = 0.1;
        for (let y = 0; y < trail_map.length; y++) {
            for (let x = 0; x < trail_map[0].length; x++) {
                maxTrail = Math.max(maxTrail, trail_map[y][x]);
            }
        }
        
        // Create an offscreen canvas for the glow effect
        const offCanvas = document.createElement('canvas');
        offCanvas.width = canvas.width;
        offCanvas.height = canvas.height;
        const offCtx = offCanvas.getContext('2d');
        
        // Draw trails on the offscreen canvas
        const imageData = offCtx.createImageData(canvas.width, canvas.height);
        const data = imageData.data;
        
        for (let y = 0; y < trail_map.length; y++) {
            for (let x = 0; x < trail_map[0].length; x++) {
                const idx = (y * canvas.width + x) * 4;
                const value = trail_map[y][x] / maxTrail;
                
                if (value > 0.01) {
                    // Green-yellow gradient based on trail strength
                    const green = Math.min(255, 50 + 150 * value);
                    const red = Math.min(255, 50 * value + (value > 0.5 ? 200 * (value - 0.5) * 2 : 0));
                    
                    data[idx] = red;     // R
                    data[idx + 1] = green; // G
                    data[idx + 2] = 50;    // B
                    data[idx + 3] = Math.min(255, 255 * value); // Alpha
                }
            }
        }
        
        offCtx.putImageData(imageData, 0, 0);
        
        // Apply a subtle blur for the glow effect
        offCtx.filter = 'blur(2px)';
        offCtx.globalCompositeOperation = 'lighten';
        offCtx.drawImage(offCanvas, 0, 0);
        offCtx.filter = 'none';
        
        // Draw the trails to the main canvas
        ctx.drawImage(offCanvas, 0, 0);
        
        // Draw food
        foodCount = 0;
        for (let y = 0; y < food_map.length; y++) {
            for (let x = 0; x < food_map[0].length; x++) {
                if (food_map[y][x]) {
                    foodCount++;
                    
                    // Draw food as a white circle with glow
                    ctx.fillStyle = colors.food;
                    ctx.beginPath();
                    ctx.arc(x, y, 3, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // Add glow
                    const gradient = ctx.createRadialGradient(x, y, 1, x, y, 8);
                    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.6)');
                    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(x, y, 8, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
        }
        
        // Draw nucleus
        if (nucleus) {
            const { x, y, size } = nucleus;
            
            // Draw nucleus as a yellow circle with glow
            ctx.fillStyle = colors.nucleus;
            ctx.beginPath();
            ctx.arc(x, y, size / 2, 0, Math.PI * 2);
            ctx.fill();
            
            // Add glow
            const gradient = ctx.createRadialGradient(x, y, size / 2 - 2, x, y, size);
            gradient.addColorStop(0, 'rgba(255, 255, 0, 0.7)');
            gradient.addColorStop(1, 'rgba(255, 255, 0, 0)');
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Calculate network metrics
        calculateNetworkMetrics(trail_map);
        
        // Update stats display
        statsDisplay.textContent = `Network length: ${networkLength.toFixed(0)} | Food found: ${foodCount}`;
    }
    
    function calculateNetworkMetrics(trail_map) {
        // Simple measure of network length - sum of significant trail values
        networkLength = 0;
        const threshold = 0.5; // Only count strong trails as part of the network
        
        for (let y = 0; y < trail_map.length; y++) {
            for (let x = 0; x < trail_map[0].length; x++) {
                if (trail_map[y][x] > threshold) {
                    networkLength++;
                }
            }
        }
    }
    
    function initCanvas() {
        // Set canvas size
        canvas.width = 800;
        canvas.height = 600;
        
        // Initial clear
        ctx.fillStyle = colors.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    
    function setupSliders() {
        // Set up all slider input listeners
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            const valueDisplay = slider.nextElementSibling;
            
            // Set initial value
            updateDisplayValue(slider, valueDisplay);
            
            // Update value display on change
            slider.addEventListener('input', () => {
                updateDisplayValue(slider, valueDisplay);
            });
        });
    }
    
    function updateDisplayValue(slider, display) {
        let value = slider.value;
        
        // Add unit for angle
        if (slider.id === 'sensor-angle') {
            value += '°';
        }
        
        display.textContent = value;
    }
    
    function updateSliderValues() {
        document.getElementById('num-agents').value = config.num_agents;
        document.getElementById('agent-speed').value = config.agent_speed;
        document.getElementById('sensor-angle').value = config.sensor_angle;
        document.getElementById('sensor-distance').value = config.sensor_distance;
        document.getElementById('turn-speed').value = config.turn_speed;
        document.getElementById('trail-strength').value = config.trail_strength;
        document.getElementById('trail-evaporation').value = config.trail_evaporation_rate;
        document.getElementById('trail-diffusion').value = config.trail_diffusion_rate;
        document.getElementById('food-quantity').value = config.food_quantity;
        document.getElementById('food-spawn-rate').value = config.food_spawn_rate;
        document.getElementById('nucleus-size').value = config.nucleus_size;
        
        // Update all display values
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            const valueDisplay = slider.nextElementSibling;
            updateDisplayValue(slider, valueDisplay);
        });
    }
}); 