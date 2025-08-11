class SatelliteInterlinkApp {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.earth = null;
        this.satellites = [];
        this.interlinkLines = [];
        this.currentData = null;
        
        this.init();
        this.setupEventListeners();
        this.setDefaultDates();
    }

    init() {
        // Initialize Three.js scene
        this.initThreeJS();
        
        // Start animation loop
        this.animate();
    }

    initThreeJS() {
        const container = document.getElementById('visualization');
        
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000011);
        
        // Camera setup
        this.camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        this.camera.position.set(0, 0, 5);
        
        // Renderer setup
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // Clear container and add renderer
        container.innerHTML = '';
        container.appendChild(this.renderer.domElement);
        
        // Add lights
        this.setupLights();
        
        // Add Earth
        this.createEarth();
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    setupLights() {
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 3, 5);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);
    }

    createEarth() {
        // Create Earth geometry
        const earthGeometry = new THREE.SphereGeometry(1, 32, 32);
        
        // Create Earth material with texture
        const earthMaterial = new THREE.MeshPhongMaterial({
            color: 0x2233ff,
            transparent: true,
            opacity: 0.8
        });
        
        this.earth = new THREE.Mesh(earthGeometry, earthMaterial);
        this.earth.receiveShadow = true;
        this.scene.add(this.earth);
        
        // Add atmosphere
        const atmosphereGeometry = new THREE.SphereGeometry(1.1, 32, 32);
        const atmosphereMaterial = new THREE.MeshPhongMaterial({
            color: 0x4488ff,
            transparent: true,
            opacity: 0.1
        });
        const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
        this.scene.add(atmosphere);
    }

    createSatellite(name, position, color = 0xff0000) {
        // Remove existing satellite with same name
        this.removeSatellite(name);
        
        // Create satellite geometry
        const satelliteGeometry = new THREE.SphereGeometry(0.02, 16, 16);
        const satelliteMaterial = new THREE.MeshPhongMaterial({ color: color });
        const satellite = new THREE.Mesh(satelliteGeometry, satelliteMaterial);
        
        // Position satellite
        satellite.position.copy(position);
        satellite.castShadow = true;
        
        // Add satellite to scene
        this.scene.add(satellite);
        
        // Store reference
        this.satellites.push({ name, mesh: satellite, position: position.clone() });
        
        // Add label
        this.addSatelliteLabel(name, position);
        
        return satellite;
    }

    addSatelliteLabel(name, position) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;
        
        context.fillStyle = 'rgba(0, 0, 0, 0.8)';
        context.fillRect(0, 0, canvas.width, canvas.height);
        
        context.fillStyle = 'white';
        context.font = '24px Arial';
        context.textAlign = 'center';
        context.fillText(name, canvas.width / 2, canvas.height / 2 + 8);
        
        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(material);
        
        sprite.position.copy(position);
        sprite.position.y += 0.1;
        sprite.scale.set(0.5, 0.125, 1);
        
        this.scene.add(sprite);
        this.satellites.push({ name: name + '_label', mesh: sprite, position: position.clone() });
    }

    removeSatellite(name) {
        this.satellites = this.satellites.filter(sat => {
            if (sat.name === name || sat.name === name + '_label') {
                this.scene.remove(sat.mesh);
                return false;
            }
            return true;
        });
    }

    clearInterlinkLines() {
        this.interlinkLines.forEach(line => {
            this.scene.remove(line);
        });
        this.interlinkLines = [];
    }

    createInterlinkLine(startPos, endPos, color = 0x00ff00) {
        const geometry = new THREE.BufferGeometry().setFromPoints([startPos, endPos]);
        const material = new THREE.LineBasicMaterial({ color: color, transparent: true, opacity: 0.6 });
        const line = new THREE.Line(geometry, material);
        
        this.scene.add(line);
        this.interlinkLines.push(line);
        
        return line;
    }

    updateSatellitePositions(positions) {
        // Clear existing satellites
        this.satellites.forEach(sat => {
            this.scene.remove(sat.mesh);
        });
        this.satellites = [];
        
        // Clear interlink lines
        this.clearInterlinkLines();
        
        if (positions.sat1) {
            const pos1 = this.latLonTo3D(positions.sat1.lat, positions.sat1.lon, positions.sat1.altitude);
            this.createSatellite('Satellite 1', pos1, 0xff0000);
        }
        
        if (positions.sat2) {
            const pos2 = this.latLonTo3D(positions.sat2.lat, positions.sat2.lon, positions.sat2.altitude);
            this.createSatellite('Satellite 2', pos2, 0x00ff00);
        }
        
        // Create interlink line if both satellites exist
        if (positions.sat1 && positions.sat2) {
            const pos1 = this.latLonTo3D(positions.sat1.lat, positions.sat1.lon, positions.sat1.altitude);
            const pos2 = this.latLonTo3D(positions.sat2.lat, positions.sat2.lon, positions.sat2.altitude);
            this.createInterlinkLine(pos1, pos2);
        }
    }

    latLonTo3D(lat, lon, altitude) {
        // Convert latitude, longitude, and altitude to 3D position
        const phi = (90 - lat) * Math.PI / 180;
        const theta = (lon + 180) * Math.PI / 180;
        
        const radius = 1 + (altitude / 6371); // Earth radius + altitude in Earth radii
        
        const x = -radius * Math.sin(phi) * Math.cos(theta);
        const y = radius * Math.cos(phi);
        const z = radius * Math.sin(phi) * Math.sin(theta);
        
        return new THREE.Vector3(x, y, z);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Rotate Earth
        if (this.earth) {
            this.earth.rotation.y += 0.001;
        }
        
        // Render scene
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    }

    onWindowResize() {
        const container = document.getElementById('visualization');
        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }

    setupEventListeners() {
        // Form submission
        document.getElementById('tleForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateInterlink();
        });
        
        // Camera controls
        this.setupCameraControls();
    }

    setupCameraControls() {
        const container = document.getElementById('visualization');
        let isMouseDown = false;
        let mouseX = 0;
        let mouseY = 0;
        
        container.addEventListener('mousedown', (e) => {
            isMouseDown = true;
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        
        container.addEventListener('mouseup', () => {
            isMouseDown = false;
        });
        
        container.addEventListener('mousemove', (e) => {
            if (isMouseDown) {
                const deltaX = e.clientX - mouseX;
                const deltaY = e.clientY - mouseY;
                
                this.camera.position.x += deltaX * 0.01;
                this.camera.position.y -= deltaY * 0.01;
                
                this.camera.lookAt(0, 0, 0);
                
                mouseX = e.clientX;
                mouseY = e.clientY;
            }
        });
        
        // Zoom with mouse wheel
        container.addEventListener('wheel', (e) => {
            const zoomSpeed = 0.1;
            const distance = this.camera.position.length();
            
            if (e.deltaY > 0) {
                this.camera.position.multiplyScalar(1 + zoomSpeed);
            } else {
                this.camera.position.multiplyScalar(1 - zoomSpeed);
            }
        });
    }

    setDefaultDates() {
        const now = new Date();
        const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        
        document.getElementById('startDate').value = now.toISOString().slice(0, 16);
        document.getElementById('endDate').value = tomorrow.toISOString().slice(0, 16);
    }

    async calculateInterlink() {
        // Show loading modal
        const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        loadingModal.show();
        
        try {
            // Collect form data
            const formData = {
                sat1_name: document.getElementById('sat1Name').value,
                sat1_tle1: document.getElementById('sat1TLE1').value,
                sat1_tle2: document.getElementById('sat1TLE2').value,
                sat2_name: document.getElementById('sat2Name').value,
                sat2_tle1: document.getElementById('sat2TLE1').value,
                sat2_tle2: document.getElementById('sat2TLE2').value,
                start_date: document.getElementById('startDate').value,
                end_date: document.getElementById('endDate').value
            };
            
            // Validate TLE data
            if (!this.validateTLE(formData)) {
                throw new Error('Invalid TLE data provided');
            }
            
            // Make API call
            const response = await fetch('/api/calculate-interlink', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayResults(result);
                this.updateVisualization(result.initial_positions);
            } else {
                throw new Error(result.error);
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert('Error calculating interlink windows: ' + error.message);
        } finally {
            loadingModal.hide();
        }
    }

    validateTLE(formData) {
        // Basic TLE validation
        const requiredFields = ['sat1_tle1', 'sat1_tle2', 'sat2_tle1', 'sat2_tle2', 'start_date', 'end_date'];
        
        for (const field of requiredFields) {
            if (!formData[field] || formData[field].trim() === '') {
                return false;
            }
        }
        
        // Check TLE format (basic check)
        const tleLines = [formData.sat1_tle1, formData.sat1_tle2, formData.sat2_tle1, formData.sat2_tle2];
        
        for (const line of tleLines) {
            if (line.length < 50) {
                return false;
            }
        }
        
        return true;
    }

    displayResults(result) {
        // Show results card
        document.getElementById('resultsCard').style.display = 'block';
        document.getElementById('windowsCard').style.display = 'block';
        
        // Update results summary
        const summary = document.getElementById('resultsSummary');
        summary.innerHTML = `
            <div class="row text-center">
                <div class="col-6">
                    <h4 class="text-primary">${result.total_windows}</h4>
                    <small class="text-muted">Interlink Windows</small>
                </div>
                <div class="col-6">
                    <h4 class="text-success">${result.total_windows > 0 ? 'Yes' : 'No'}</h4>
                    <small class="text-muted">Communication Possible</small>
                </div>
            </div>
        `;
        
        // Update windows table
        this.updateWindowsTable(result.interlink_windows);
        
        // Store current data
        this.currentData = result;
    }

    updateWindowsTable(windows) {
        const tbody = document.getElementById('windowsTableBody');
        tbody.innerHTML = '';
        
        windows.forEach((window, index) => {
            const row = document.createElement('tr');
            row.className = 'fade-in';
            row.style.animationDelay = `${index * 0.1}s`;
            
            const timestamp = new Date(window.timestamp).toLocaleString();
            const distance = window.distance.toFixed(2);
            const sat1Pos = `${window.sat1_pos.lat.toFixed(2)}°, ${window.sat1_pos.lon.toFixed(2)}°`;
            const sat2Pos = `${window.sat2_pos.lat.toFixed(2)}°, ${window.sat2_pos.lon.toFixed(2)}°`;
            
            row.innerHTML = `
                <td>${timestamp}</td>
                <td>${distance}</td>
                <td>${sat1Pos}</td>
                <td>${sat2Pos}</td>
                <td><span class="badge badge-success">Active</span></td>
            `;
            
            tbody.appendChild(row);
        });
    }

    updateVisualization(positions) {
        if (positions) {
            this.updateSatellitePositions(positions);
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SatelliteInterlinkApp();
});
