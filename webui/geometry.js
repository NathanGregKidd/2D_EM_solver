/**
 * 2D Transmission Line Geometry Designer
 * JavaScript implementation for drawing and manipulating transmission line geometries
 */

class TransmissionLineGeometry {
    constructor() {
        this.canvas = document.getElementById('geometry-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.scale = 0.1; // pixels per micrometer
        this.offsetX = 50;
        this.offsetY = 50;
        
        // Zoom and pan state
        this.zoomLevel = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.minZoom = 0.1;
        this.maxZoom = 10;
        
        // Pan interaction state
        this.isPanning = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        
        // Set initial canvas cursor
        this.canvas.style.cursor = 'grab';
        
        this.initializeEventListeners();
        this.updateZoomDisplay();
        this.drawGeometry();
    }
    
    initializeEventListeners() {
        // Control updates
        document.getElementById('line-type').addEventListener('change', () => this.updateGeometry());
        document.getElementById('trace-width').addEventListener('input', () => this.updateGeometry());
        document.getElementById('trace-height').addEventListener('input', () => this.updateGeometry());
        document.getElementById('ground-thickness').addEventListener('input', () => this.updateGeometry());
        document.getElementById('coplanar-gap').addEventListener('input', () => this.updateGeometry());
        document.getElementById('substrate-height').addEventListener('input', () => this.updateGeometry());
        document.getElementById('substrate-width').addEventListener('input', () => this.updateGeometry());
        document.getElementById('air-height').addEventListener('input', () => this.updateGeometry());
        document.getElementById('substrate-er').addEventListener('input', () => this.updateEstimatedParams());
        document.getElementById('substrate-loss').addEventListener('input', () => this.updateEstimatedParams());
        document.getElementById('conductor-sigma').addEventListener('input', () => this.updateEstimatedParams());
        
        // Buttons
        document.getElementById('redraw-btn').addEventListener('click', () => this.drawGeometry());
        document.getElementById('export-btn').addEventListener('click', () => this.showExportModal());
        document.getElementById('clear-btn').addEventListener('click', () => this.clearCanvas());
        
        // Zoom controls
        document.getElementById('zoom-in-btn').addEventListener('click', () => this.zoomIn());
        document.getElementById('zoom-out-btn').addEventListener('click', () => this.zoomOut());
        document.getElementById('zoom-reset-btn').addEventListener('click', () => this.resetZoom());
        
        // Canvas zoom and pan interactions
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e));
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.handleMouseUp());
        this.canvas.addEventListener('mouseleave', () => this.handleMouseUp());
        
        // Modal controls
        document.getElementById('copy-data-btn').addEventListener('click', () => this.copyExportData());
        document.getElementById('download-data-btn').addEventListener('click', () => this.downloadExportData());
        
        // Modal close
        document.querySelector('.close').addEventListener('click', () => this.hideExportModal());
        document.getElementById('export-modal').addEventListener('click', (e) => {
            if (e.target.id === 'export-modal') {
                this.hideExportModal();
            }
        });
    }
    
    // Zoom and pan methods
    handleWheel(e) {
        e.preventDefault();
        
        // Get mouse position relative to canvas
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        // Calculate zoom factor
        const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
        const newZoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.zoomLevel * zoomFactor));
        
        // Adjust pan to zoom towards mouse position
        const zoomRatio = newZoom / this.zoomLevel;
        this.panX = mouseX - (mouseX - this.panX) * zoomRatio;
        this.panY = mouseY - (mouseY - this.panY) * zoomRatio;
        
        this.zoomLevel = newZoom;
        this.updateZoomDisplay();
        this.drawGeometry();
    }
    
    handleMouseDown(e) {
        this.isPanning = true;
        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;
        this.canvas.style.cursor = 'grabbing';
    }
    
    handleMouseMove(e) {
        if (this.isPanning) {
            const deltaX = e.clientX - this.lastMouseX;
            const deltaY = e.clientY - this.lastMouseY;
            
            this.panX += deltaX;
            this.panY += deltaY;
            
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
            
            this.drawGeometry();
        }
    }
    
    handleMouseUp() {
        this.isPanning = false;
        this.canvas.style.cursor = 'grab';
    }
    
    zoomIn() {
        const newZoom = Math.min(this.maxZoom, this.zoomLevel * 1.2);
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        const zoomRatio = newZoom / this.zoomLevel;
        this.panX = centerX - (centerX - this.panX) * zoomRatio;
        this.panY = centerY - (centerY - this.panY) * zoomRatio;
        
        this.zoomLevel = newZoom;
        this.updateZoomDisplay();
        this.drawGeometry();
    }
    
    zoomOut() {
        const newZoom = Math.max(this.minZoom, this.zoomLevel / 1.2);
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        const zoomRatio = newZoom / this.zoomLevel;
        this.panX = centerX - (centerX - this.panX) * zoomRatio;
        this.panY = centerY - (centerY - this.panY) * zoomRatio;
        
        this.zoomLevel = newZoom;
        this.updateZoomDisplay();
        this.drawGeometry();
    }
    
    resetZoom() {
        this.zoomLevel = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.updateZoomDisplay();
        this.drawGeometry();
    }
    
    updateZoomDisplay() {
        const zoomPercent = Math.round(this.zoomLevel * 100);
        document.getElementById('zoom-level').textContent = `${zoomPercent}%`;
    }
    
    updateGeometry() {
        this.drawGeometry();
        this.updateEstimatedParams();
    }
    
    clearCanvas() {
        // Clear the entire canvas without transformations
        this.ctx.save();
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.restore();
        
        // Draw grid with transformations
        this.drawGrid();
    }
    
    drawGrid() {
        this.ctx.save();
        this.ctx.translate(this.panX, this.panY);
        this.ctx.scale(this.zoomLevel, this.zoomLevel);
        
        const ctx = this.ctx;
        const gridSize = 50; // pixels
        
        ctx.strokeStyle = '#f0f0f0';
        ctx.lineWidth = 1 / this.zoomLevel; // Adjust line width for zoom
        
        // Calculate visible grid range
        const startX = Math.floor(-this.panX / this.zoomLevel / gridSize) * gridSize;
        const endX = Math.ceil((this.canvas.width - this.panX) / this.zoomLevel / gridSize) * gridSize;
        const startY = Math.floor(-this.panY / this.zoomLevel / gridSize) * gridSize;
        const endY = Math.ceil((this.canvas.height - this.panY) / this.zoomLevel / gridSize) * gridSize;
        
        // Vertical lines
        for (let x = startX; x <= endX; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, startY);
            ctx.lineTo(x, endY);
            ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = startY; y <= endY; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(startX, y);
            ctx.lineTo(endX, y);
            ctx.stroke();
        }
        
        this.ctx.restore();
    }
    
    drawGeometry() {
        // Clear canvas
        this.clearCanvas();
        
        // Save context state
        this.ctx.save();
        
        // Apply zoom and pan transformations
        this.ctx.translate(this.panX, this.panY);
        this.ctx.scale(this.zoomLevel, this.zoomLevel);
        
        // Get current parameters
        const params = this.getGeometryParams();
        
        // Convert dimensions to pixels
        const traceWidth = params.traceWidth * this.scale;
        const traceHeight = params.traceHeight * this.scale;
        const substrateWidth = params.substrateWidth * this.scale;
        const substrateHeight = params.substrateHeight * this.scale;
        const airHeight = params.airHeight * this.scale;
        
        // Calculate positions
        const canvasCenterX = this.canvas.width / 2;
        const substrateY = this.canvas.height - this.offsetY - substrateHeight;
        const substrateX = canvasCenterX - substrateWidth / 2;
        const traceX = canvasCenterX - traceWidth / 2;
        const traceY = substrateY - traceHeight;
        
        // Calculate the top of the geometry based on transmission line type
        let geometryTopY;
        switch (params.lineType) {
            case 'stripline':
                // Top ground plane is above substrate
                geometryTopY = substrateY - 20;
                break;
            case 'microstrip':
            case 'coplanar':
            case 'coplanar-with-ground':
            case 'grounded-coplanar':
            case 'custom':
            default:
                // Trace is on top of substrate
                geometryTopY = traceY;
                break;
        }
        
        // Calculate air box position (sits on top of the geometry)
        const airBoxY = geometryTopY - airHeight;
        
        // Draw substrate
        this.ctx.fillStyle = '#27ae60'; // Green for substrate
        this.ctx.fillRect(substrateX, substrateY, substrateWidth, substrateHeight);
        this.ctx.strokeStyle = '#1e8449';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(substrateX, substrateY, substrateWidth, substrateHeight);
        
        // Draw air/vacuum region that wraps around top-layer elements
        this.drawAirRegion(params.lineType, traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight, airBoxY, airHeight, params.coplanarGap * this.scale);
        
        // Draw trace based on transmission line type
        this.drawTrace(params.lineType, traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight, params.groundThickness * this.scale, params.coplanarGap * this.scale);
        
        // Add dimensions annotations
        this.drawDimensions(traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight, params);
        
        // Add coordinate system
        this.drawCoordinateSystem();
        
        // Restore context state
        this.ctx.restore();
    }
    
    drawAirRegion(lineType, traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight, airBoxY, airHeight, coplanarGap = 20) {
        this.ctx.fillStyle = '#ecf0f1'; // Light gray for air
        this.ctx.strokeStyle = '#bdc3c7';
        this.ctx.lineWidth = 1;
        
        const groundWidth = 50; // pixels (matches trace drawing)
        
        switch (lineType) {
            case 'microstrip':
                // Air wraps around the trace - fills left, top, and right regions
                // Left air region (from substrate edge to trace)
                this.ctx.fillRect(substrateX, airBoxY, traceX - substrateX, airHeight + traceHeight);
                this.ctx.strokeRect(substrateX, airBoxY, traceX - substrateX, airHeight + traceHeight);
                
                // Top air region (above the trace)
                this.ctx.fillRect(traceX, airBoxY, traceWidth, traceY - airBoxY);
                this.ctx.strokeRect(traceX, airBoxY, traceWidth, traceY - airBoxY);
                
                // Right air region (from trace to substrate edge)
                this.ctx.fillRect(traceX + traceWidth, airBoxY, (substrateX + substrateWidth) - (traceX + traceWidth), airHeight + traceHeight);
                this.ctx.strokeRect(traceX + traceWidth, airBoxY, (substrateX + substrateWidth) - (traceX + traceWidth), airHeight + traceHeight);
                break;
                
            case 'stripline':
                // For stripline, there's no exposed air on top since it's enclosed by ground planes
                // The top ground plane covers everything
                // No air region to draw
                break;
                
            case 'coplanar':
            case 'coplanar-with-ground':
            case 'grounded-coplanar':
                // Air wraps around coplanar structure - fills between and around ground planes
                const leftGroundX = traceX - coplanarGap - groundWidth;
                const rightGroundX = traceX + traceWidth + coplanarGap;
                
                // Left air region (from substrate edge to left ground)
                this.ctx.fillRect(substrateX, airBoxY, leftGroundX - substrateX, airHeight+traceHeight);
                this.ctx.strokeRect(substrateX, airBoxY, leftGroundX - substrateX, airHeight+traceHeight);

                // Gap between left ground and trace
                this.ctx.fillRect(leftGroundX + groundWidth, airBoxY, coplanarGap, airHeight+traceHeight);
                this.ctx.strokeRect(leftGroundX + groundWidth, airBoxY, coplanarGap, airHeight+traceHeight);
                
                // Above trace
                this.ctx.fillRect(traceX, airBoxY, traceWidth, traceY - airBoxY);
                this.ctx.strokeRect(traceX, airBoxY, traceWidth, traceY - airBoxY);
                
                // Above left ground
                this.ctx.fillRect(leftGroundX, airBoxY, groundWidth, traceY - airBoxY);
                this.ctx.strokeRect(leftGroundX, airBoxY, groundWidth, traceY - airBoxY);
                
                // Above right ground  
                this.ctx.fillRect(rightGroundX, airBoxY, groundWidth, traceY - airBoxY);
                this.ctx.strokeRect(rightGroundX, airBoxY, groundWidth, traceY - airBoxY);
                
                // Gap between trace and right ground
                this.ctx.fillRect(traceX + traceWidth, airBoxY, coplanarGap, airHeight+traceHeight);
                this.ctx.strokeRect(traceX + traceWidth, airBoxY, coplanarGap, airHeight+traceHeight);

                // Right air region (from right ground to substrate edge)
                this.ctx.fillRect(rightGroundX + groundWidth, airBoxY, (substrateX + substrateWidth) - (rightGroundX + groundWidth), airHeight+traceHeight);
                this.ctx.strokeRect(rightGroundX + groundWidth, airBoxY, (substrateX + substrateWidth) - (rightGroundX + groundWidth), airHeight+traceHeight);
                break;
                
            case 'custom':
                // For custom, wrap around the trace similar to microstrip
                // Left air region
                this.ctx.fillRect(substrateX, airBoxY, traceX - substrateX, airHeight);
                this.ctx.strokeRect(substrateX, airBoxY, traceX - substrateX, airHeight);
                
                // Top air region
                this.ctx.fillRect(traceX, airBoxY, traceWidth, traceY - airBoxY);
                this.ctx.strokeRect(traceX, airBoxY, traceWidth, traceY - airBoxY);
                
                // Right air region
                this.ctx.fillRect(traceX + traceWidth, airBoxY, (substrateX + substrateWidth) - (traceX + traceWidth), airHeight);
                this.ctx.strokeRect(traceX + traceWidth, airBoxY, (substrateX + substrateWidth) - (traceX + traceWidth), airHeight);
                break;
        }
    }
    
    drawTrace(lineType, traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight, groundThickness = 0, coplanarGap = 20) {
        this.ctx.fillStyle = '#e67e22'; // Orange for conductor
        this.ctx.strokeStyle = '#d35400';
        this.ctx.lineWidth = 2;
        
        switch (lineType) {
            case 'microstrip':
                // Signal trace on top of substrate
                this.ctx.fillRect(traceX, traceY, traceWidth, traceHeight);
                this.ctx.strokeRect(traceX, traceY, traceWidth, traceHeight);
                
                // Ground plane below substrate (different color)
                this.ctx.fillStyle = '#8b4513'; // Brown for ground plane
                this.ctx.strokeStyle = '#654321';
                this.ctx.fillRect(substrateX, substrateY + substrateHeight, substrateWidth, groundThickness);
                this.ctx.strokeRect(substrateX, substrateY + substrateHeight, substrateWidth, groundThickness);
                break;
                
            case 'stripline':
                // Trace embedded in substrate with ground planes
                const embeddedTraceY = substrateY + substrateHeight / 2 - traceHeight / 2;
                
                // Top ground plane
                this.ctx.fillRect(substrateX, substrateY - 20, substrateWidth, 15);
                this.ctx.strokeRect(substrateX, substrateY - 20, substrateWidth, 15);
                
                // Bottom ground plane
                this.ctx.fillRect(substrateX, substrateY + substrateHeight + 5, substrateWidth, 15);
                this.ctx.strokeRect(substrateX, substrateY + substrateHeight + 5, substrateWidth, 15);
                
                // Signal trace
                this.ctx.fillRect(traceX, embeddedTraceY, traceWidth, traceHeight);
                this.ctx.strokeRect(traceX, embeddedTraceY, traceWidth, traceHeight);
                break;
                
            case 'coplanar':
                // Trace with side ground planes
                const groundWidth = 50; // pixels
                
                // Signal trace
                this.ctx.fillRect(traceX, traceY, traceWidth, traceHeight);
                this.ctx.strokeRect(traceX, traceY, traceWidth, traceHeight);
                
                // Left ground plane
                this.ctx.fillRect(traceX - coplanarGap - groundWidth, traceY, groundWidth, traceHeight);
                this.ctx.strokeRect(traceX - coplanarGap - groundWidth, traceY, groundWidth, traceHeight);
                
                // Right ground plane
                this.ctx.fillRect(traceX + traceWidth + coplanarGap, traceY, groundWidth, traceHeight);
                this.ctx.strokeRect(traceX + traceWidth + coplanarGap, traceY, groundWidth, traceHeight);
                break;
                
            case 'coplanar-with-ground':
                // Coplanar waveguide with ground plane below substrate
                const groundWidthWG = 50; // pixels
                
                // Signal trace
                this.ctx.fillRect(traceX, traceY, traceWidth, traceHeight);
                this.ctx.strokeRect(traceX, traceY, traceWidth, traceHeight);
                
                // Left ground plane (coplanar)
                this.ctx.fillRect(traceX - coplanarGap - groundWidthWG, traceY, groundWidthWG, traceHeight);
                this.ctx.strokeRect(traceX - coplanarGap - groundWidthWG, traceY, groundWidthWG, traceHeight);
                
                // Right ground plane (coplanar)
                this.ctx.fillRect(traceX + traceWidth + coplanarGap, traceY, groundWidthWG, traceHeight);
                this.ctx.strokeRect(traceX + traceWidth + coplanarGap, traceY, groundWidthWG, traceHeight);
                
                // Ground plane below substrate (different color)
                this.ctx.fillStyle = '#8b4513'; // Brown for ground plane
                this.ctx.strokeStyle = '#654321';
                this.ctx.fillRect(substrateX, substrateY + substrateHeight, substrateWidth, groundThickness);
                this.ctx.strokeRect(substrateX, substrateY + substrateHeight, substrateWidth, groundThickness);
                break;
                
            case 'grounded-coplanar':
                // Grounded coplanar waveguide with vias connecting ground planes
                const groundWidthGC = 50; // pixels
                
                // Signal trace
                this.ctx.fillRect(traceX, traceY, traceWidth, traceHeight);
                this.ctx.strokeRect(traceX, traceY, traceWidth, traceHeight);
                
                // Left ground plane (coplanar)
                this.ctx.fillRect(traceX - coplanarGap - groundWidthGC, traceY, groundWidthGC, traceHeight);
                this.ctx.strokeRect(traceX - coplanarGap - groundWidthGC, traceY, groundWidthGC, traceHeight);
                
                // Right ground plane (coplanar)
                this.ctx.fillRect(traceX + traceWidth + coplanarGap, traceY, groundWidthGC, traceHeight);
                this.ctx.strokeRect(traceX + traceWidth + coplanarGap, traceY, groundWidthGC, traceHeight);
                
                // Ground plane below substrate (different color)
                this.ctx.fillStyle = '#8b4513'; // Brown for ground plane
                this.ctx.strokeStyle = '#654321';
                this.ctx.fillRect(substrateX, substrateY + substrateHeight, substrateWidth, groundThickness);
                this.ctx.strokeRect(substrateX, substrateY + substrateHeight, substrateWidth, groundThickness);
                
                // Vias connecting coplanar grounds to bottom ground plane
                this.ctx.fillStyle = '#666666'; // Gray for vias
                this.ctx.strokeStyle = '#444444';
                const viaRadius = 3;
                const viaSpacing = 40; // pixels
                
                // Left side vias
                for (let y = traceY + traceHeight; y <= substrateY + substrateHeight; y += viaSpacing) {
                    if (y + viaRadius <= substrateY + substrateHeight) {
                        this.ctx.beginPath();
                        this.ctx.arc(traceX - coplanarGap - groundWidthGC/2, y, viaRadius, 0, 2 * Math.PI);
                        this.ctx.fill();
                        this.ctx.stroke();
                    }
                }
                
                // Right side vias
                for (let y = traceY + traceHeight; y <= substrateY + substrateHeight; y += viaSpacing) {
                    if (y + viaRadius <= substrateY + substrateHeight) {
                        this.ctx.beginPath();
                        this.ctx.arc(traceX + traceWidth + coplanarGap + groundWidthGC/2, y, viaRadius, 0, 2 * Math.PI);
                        this.ctx.fill();
                        this.ctx.stroke();
                    }
                }
                break;
                
            case 'custom':
                // Basic trace for custom (user can extend this)
                this.ctx.fillRect(traceX, traceY, traceWidth, traceHeight);
                this.ctx.strokeRect(traceX, traceY, traceWidth, traceHeight);
                break;
        }
    }
    
    drawDimensions(traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight, params) {
        this.ctx.strokeStyle = '#333';
        this.ctx.fillStyle = '#333';
        this.ctx.lineWidth = 1;
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        
        // Trace width dimension
        const traceWidthText = `W = ${params.traceWidth} μm`;
        this.ctx.fillText(traceWidthText, traceX + traceWidth / 2, traceY - 10);
        
        // Draw dimension line for trace width
        this.ctx.beginPath();
        this.ctx.moveTo(traceX, traceY - 5);
        this.ctx.lineTo(traceX, traceY - 15);
        this.ctx.moveTo(traceX + traceWidth, traceY - 5);
        this.ctx.lineTo(traceX + traceWidth, traceY - 15);
        this.ctx.moveTo(traceX, traceY - 12);
        this.ctx.lineTo(traceX + traceWidth, traceY - 12);
        this.ctx.stroke();
        
        // Substrate height dimension
        this.ctx.textAlign = 'left';
        const subHeightText = `H = ${params.substrateHeight} μm`;
        this.ctx.fillText(subHeightText, substrateX + substrateWidth + 10, substrateY + substrateHeight / 2);
        
        // Draw dimension line for substrate height
        this.ctx.beginPath();
        this.ctx.moveTo(substrateX + substrateWidth + 5, substrateY);
        this.ctx.lineTo(substrateX + substrateWidth + 15, substrateY);
        this.ctx.moveTo(substrateX + substrateWidth + 5, substrateY + substrateHeight);
        this.ctx.lineTo(substrateX + substrateWidth + 15, substrateY + substrateHeight);
        this.ctx.moveTo(substrateX + substrateWidth + 10, substrateY);
        this.ctx.lineTo(substrateX + substrateWidth + 10, substrateY + substrateHeight);
        this.ctx.stroke();
    }
    
    drawCoordinateSystem() {
        this.ctx.strokeStyle = '#333';
        this.ctx.fillStyle = '#333';
        this.ctx.lineWidth = 2;
        this.ctx.font = '14px Arial';
        
        // Draw axes
        const originX = 30;
        const originY = this.canvas.height - 30;
        const axisLength = 40;
        
        // X-axis
        this.ctx.beginPath();
        this.ctx.moveTo(originX, originY);
        this.ctx.lineTo(originX + axisLength, originY);
        this.ctx.stroke();
        
        // Y-axis
        this.ctx.beginPath();
        this.ctx.moveTo(originX, originY);
        this.ctx.lineTo(originX, originY - axisLength);
        this.ctx.stroke();
        
        // Arrow heads
        this.ctx.beginPath();
        this.ctx.moveTo(originX + axisLength - 5, originY - 3);
        this.ctx.lineTo(originX + axisLength, originY);
        this.ctx.lineTo(originX + axisLength - 5, originY + 3);
        this.ctx.stroke();
        
        this.ctx.beginPath();
        this.ctx.moveTo(originX - 3, originY - axisLength + 5);
        this.ctx.lineTo(originX, originY - axisLength);
        this.ctx.lineTo(originX + 3, originY - axisLength + 5);
        this.ctx.stroke();
        
        // Labels
        this.ctx.textAlign = 'center';
        this.ctx.fillText('x', originX + axisLength + 10, originY + 5);
        this.ctx.fillText('y', originX - 5, originY - axisLength - 10);
    }
    
    getGeometryParams() {
        return {
            lineType: document.getElementById('line-type').value,
            traceWidth: parseFloat(document.getElementById('trace-width').value),
            traceHeight: parseFloat(document.getElementById('trace-height').value),
            groundThickness: parseFloat(document.getElementById('ground-thickness').value),
            coplanarGap: parseFloat(document.getElementById('coplanar-gap').value),
            substrateHeight: parseFloat(document.getElementById('substrate-height').value),
            substrateWidth: parseFloat(document.getElementById('substrate-width').value),
            airHeight: parseFloat(document.getElementById('air-height').value),
            substrateEr: parseFloat(document.getElementById('substrate-er').value),
            substrateLoss: parseFloat(document.getElementById('substrate-loss').value),
            conductorSigma: parseFloat(document.getElementById('conductor-sigma').value)
        };
    }
    
    updateEstimatedParams() {
        const params = this.getGeometryParams();
        
        // Simple microstrip impedance approximation (Wheeler's formula)
        let z0 = 0;
        let effEr = 0;
        
        if (params.lineType === 'microstrip') {
            const w_h = params.traceWidth / params.substrateHeight;
            const er = params.substrateEr;
            
            if (w_h <= 1) {
                z0 = (60 / Math.sqrt(er)) * Math.log(8 / w_h + w_h / 4);
            } else {
                z0 = (120 * Math.PI) / (Math.sqrt(er) * (w_h + 1.393 + 0.667 * Math.log(w_h + 1.444)));
            }
            
            effEr = (er + 1) / 2 + ((er - 1) / 2) * Math.pow(1 + 12 / w_h, -0.5);
            
        } else if (params.lineType === 'stripline') {
            const w_h = params.traceWidth / params.substrateHeight;
            const er = params.substrateEr;
            
            if (w_h <= 0.35) {
                z0 = (60 / Math.sqrt(er)) * Math.log(4 / w_h);
            } else {
                z0 = (94.15 / Math.sqrt(er)) / (w_h + 2.7);
            }
            
            effEr = er;
            
        } else if (params.lineType === 'coplanar') {
            // Basic coplanar waveguide approximation
            z0 = 50; // Simplified approximation
            effEr = (params.substrateEr + 1) / 2;
            
        } else if (params.lineType === 'coplanar-with-ground') {
            // Coplanar waveguide with ground plane - similar to coplanar but with ground influence
            z0 = 45; // Slightly lower due to ground plane influence
            effEr = (params.substrateEr + 1) / 2 + 0.1; // Slightly higher effective permittivity
            
        } else if (params.lineType === 'grounded-coplanar') {
            // Grounded coplanar waveguide - lowest impedance due to strong ground coupling
            z0 = 40; // Lower due to strong ground coupling via vias
            effEr = (params.substrateEr + 1) / 2 + 0.2; // Higher effective permittivity due to ground coupling
            
        } else {
            z0 = 50; // Default approximation
            effEr = params.substrateEr;
        }
        
        document.getElementById('z0-estimate').textContent = z0.toFixed(1) + ' Ω';
        document.getElementById('eff-er-estimate').textContent = effEr.toFixed(2);
    }
    
    showExportModal() {
        const params = this.getGeometryParams();
        const geometryData = this.buildLayeredGeometry(params);
        
        document.getElementById('export-data').value = JSON.stringify(geometryData, null, 2);
        document.getElementById('export-modal').style.display = 'block';
    }
    
    buildLayeredGeometry(params) {
        // Build the layered geometry structure based on transmission line type
        let layers = {};
        let layerCount = 0;
        let conductorCount = 0;
        
        // Material properties for conductors (copper by default)
        const copperProperties = {
            relative_permittivity: 1.0,
            relative_permeability: 0.999991,
            resistivity: 1.0 / params.conductorSigma
        };
        
        // Material properties for substrate (FR4 typical)
        const substrateProperties = {
            relative_permittivity: params.substrateEr,
            relative_permeability: 1.0,
            resistivity: 1e15 // Very high resistivity for dielectric
        };
        
        // Material properties for air
        const airProperties = {
            relative_permittivity: 1.0,
            relative_permeability: 1.0,
            resistivity: 1e16 // Very high resistivity for air
        };
        
        // Build layers based on transmission line type
        switch (params.lineType) {
            case 'microstrip':
                layers = this.buildMicrostripLayers(params, copperProperties, substrateProperties, airProperties);
                break;
            case 'stripline':
                layers = this.buildStriplineLayers(params, copperProperties, substrateProperties, airProperties);
                break;
            case 'coplanar':
                layers = this.buildCoplanarLayers(params, copperProperties, substrateProperties, airProperties);
                break;
            case 'coplanar-with-ground':
                layers = this.buildCoplanarWithGroundLayers(params, copperProperties, substrateProperties, airProperties);
                break;
            case 'grounded-coplanar':
                layers = this.buildGroundedCoplanarLayers(params, copperProperties, substrateProperties, airProperties);
                break;
            case 'custom':
                layers = this.buildCustomLayers(params, copperProperties, substrateProperties, airProperties);
                break;
            default:
                layers = this.buildMicrostripLayers(params, copperProperties, substrateProperties, airProperties);
        }
        
        // Count layers and conductors
        layerCount = Object.keys(layers).length;
        conductorCount = 0;
        for (const layerKey in layers) {
            const layer = layers[layerKey];
            if (layer.elements) {
                for (const elementKey in layer.elements) {
                    const element = layer.elements[elementKey];
                    if (element.type === 'conductor') {
                        conductorCount++;
                    }
                }
            }
        }
        
        return {
            metadata: {
                timestamp: new Date().toISOString(),
                transmissionLineType: params.lineType,
                n_layers: layerCount,
                n_conductors: conductorCount,
                estimatedParameters: {
                    characteristicImpedance_ohms: parseFloat(document.getElementById('z0-estimate').textContent),
                    effectivePermittivity: parseFloat(document.getElementById('eff-er-estimate').textContent)
                }
            },
            layers: layers
        };
    }
    
    buildMicrostripLayers(params, copperProperties, substrateProperties, airProperties) {
        const layers = {};
        
        // Layer 0: Bottom ground plane
        layers[0] = {
            elements: {
                1: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.groundThickness,
                    port_number: 0,
                    isGround: true
                }
            }
        };
        
        // Layer 1: Substrate
        layers[1] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'FR4',
                    relative_permittivity: substrateProperties.relative_permittivity,
                    relative_permeability: substrateProperties.relative_permeability,
                    resistivity: substrateProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.substrateHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        // Layer 2: Signal trace with air spacers
        const leftAirWidth = (params.substrateWidth - params.traceWidth) / 2;
        const rightAirWidth = leftAirWidth;
        
        layers[2] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: leftAirWidth,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                },
                2: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: params.traceWidth,
                    height: params.traceHeight,
                    port_number: 1,
                    isGround: false
                },
                3: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: rightAirWidth,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        // Layer 3: Top air box
        layers[3] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.airHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        return layers;
    }
    
    buildStriplineLayers(params, copperProperties, substrateProperties, airProperties) {
        const layers = {};
        
        // Layer 0: Bottom ground plane
        layers[0] = {
            elements: {
                1: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.groundThickness,
                    port_number: 0,
                    isGround: true
                }
            }
        };
        
        // Layer 1: Bottom substrate half
        layers[1] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'FR4',
                    relative_permittivity: substrateProperties.relative_permittivity,
                    relative_permeability: substrateProperties.relative_permeability,
                    resistivity: substrateProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.substrateHeight / 2,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        // Layer 2: Signal trace (embedded, centered in substrate)
        layers[2] = {
            elements: {
                1: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: params.traceWidth,
                    height: params.traceHeight,
                    port_number: 1,
                    isGround: false
                }
            }
        };
        
        // Layer 3: Top substrate half
        layers[3] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'FR4',
                    relative_permittivity: substrateProperties.relative_permittivity,
                    relative_permeability: substrateProperties.relative_permeability,
                    resistivity: substrateProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.substrateHeight / 2,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        // Layer 4: Top ground plane
        layers[4] = {
            elements: {
                1: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.groundThickness,
                    port_number: 0,
                    isGround: true
                }
            }
        };
        
        return layers;
    }
    
    buildCoplanarLayers(params, copperProperties, substrateProperties, airProperties) {
        const layers = {};
        const groundWidth = 50; // Fixed width for ground planes in pixels, needs conversion
        const groundWidthUm = groundWidth / this.scale; // Convert to micrometers
        
        // Calculate element widths for left-to-right ordering
        const leftAirWidth = (params.substrateWidth - params.traceWidth - 2 * params.coplanarGap - 2 * groundWidthUm) / 2;
        const rightAirWidth = leftAirWidth;
        
        // Layer 0: Substrate
        layers[0] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'FR4',
                    relative_permittivity: substrateProperties.relative_permittivity,
                    relative_permeability: substrateProperties.relative_permeability,
                    resistivity: substrateProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.substrateHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        // Layer 1: Coplanar structure - left air, left ground, gap, signal, gap, right ground, right air
        layers[1] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: leftAirWidth,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                },
                2: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: groundWidthUm,
                    height: params.traceHeight,
                    port_number: 0,
                    isGround: true
                },
                3: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: params.coplanarGap,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                },
                4: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: params.traceWidth,
                    height: params.traceHeight,
                    port_number: 1,
                    isGround: false
                },
                5: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: params.coplanarGap,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                },
                6: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: groundWidthUm,
                    height: params.traceHeight,
                    port_number: 0,
                    isGround: true
                },
                7: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: rightAirWidth,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        // Layer 2: Top air box
        layers[2] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.airHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        return layers;
    }
    
    buildCoplanarWithGroundLayers(params, copperProperties, substrateProperties, airProperties) {
        const layers = {};
        const groundWidth = 50; // Fixed width for ground planes
        const groundWidthUm = groundWidth / this.scale;
        
        const leftAirWidth = (params.substrateWidth - params.traceWidth - 2 * params.coplanarGap - 2 * groundWidthUm) / 2;
        const rightAirWidth = leftAirWidth;
        
        // Layer 0: Bottom ground plane
        layers[0] = {
            elements: {
                1: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.groundThickness,
                    port_number: 0,
                    isGround: true
                }
            }
        };
        
        // Layer 1: Substrate
        layers[1] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'FR4',
                    relative_permittivity: substrateProperties.relative_permittivity,
                    relative_permeability: substrateProperties.relative_permeability,
                    resistivity: substrateProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.substrateHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        // Layer 2: Coplanar structure with ground planes
        layers[2] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: leftAirWidth,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                },
                2: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: groundWidthUm,
                    height: params.traceHeight,
                    port_number: 0,
                    isGround: true
                },
                3: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: params.coplanarGap,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                },
                4: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: params.traceWidth,
                    height: params.traceHeight,
                    port_number: 1,
                    isGround: false
                },
                5: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: params.coplanarGap,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                },
                6: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: groundWidthUm,
                    height: params.traceHeight,
                    port_number: 0,
                    isGround: true
                },
                7: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: rightAirWidth,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        // Layer 3: Top air box
        layers[3] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.airHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        return layers;
    }
    
    buildGroundedCoplanarLayers(params, copperProperties, substrateProperties, airProperties) {
        // Similar to coplanar-with-ground but with via connections indicated in metadata
        return this.buildCoplanarWithGroundLayers(params, copperProperties, substrateProperties, airProperties);
    }
    
    buildCustomLayers(params, copperProperties, substrateProperties, airProperties) {
        // Basic custom structure - can be extended by users
        const layers = {};
        
        // Layer 0: Substrate
        layers[0] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'FR4',
                    relative_permittivity: substrateProperties.relative_permittivity,
                    relative_permeability: substrateProperties.relative_permeability,
                    resistivity: substrateProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.substrateHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        // Layer 1: Signal trace with air spacers
        const leftAirWidth = (params.substrateWidth - params.traceWidth) / 2;
        const rightAirWidth = leftAirWidth;
        
        layers[1] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: leftAirWidth,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                },
                2: {
                    type: 'conductor',
                    material: 'copper',
                    relative_permittivity: copperProperties.relative_permittivity,
                    relative_permeability: copperProperties.relative_permeability,
                    resistivity: copperProperties.resistivity,
                    width: params.traceWidth,
                    height: params.traceHeight,
                    port_number: 1,
                    isGround: false
                },
                3: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: rightAirWidth,
                    height: params.traceHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        // Layer 2: Top air box
        layers[2] = {
            elements: {
                1: {
                    type: 'dielectric',
                    material: 'air',
                    relative_permittivity: airProperties.relative_permittivity,
                    relative_permeability: airProperties.relative_permeability,
                    resistivity: airProperties.resistivity,
                    width: params.substrateWidth,
                    height: params.airHeight,
                    port_number: null,
                    isGround: false
                }
            }
        };
        
        return layers;
    }
    
    hideExportModal() {
        document.getElementById('export-modal').style.display = 'none';
    }
    
    copyExportData() {
        const exportData = document.getElementById('export-data');
        exportData.select();
        exportData.setSelectionRange(0, 99999);
        document.execCommand('copy');
        
        // Show feedback
        const btn = document.getElementById('copy-data-btn');
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    }
    
    downloadExportData() {
        const exportData = document.getElementById('export-data').value;
        const blob = new Blob([exportData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `transmission_line_geometry_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const geometryDesigner = new TransmissionLineGeometry();
    geometryDesigner.updateEstimatedParams(); // Calculate initial estimates
});