/**
 * 2D Transmission Line Geometry Designer
 * JavaScript implementation for drawing and manipulating transmission line geometries
 */

class TransmissionLineGeometry {
    constructor() {
        this.canvas = document.getElementById('geometry-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.scale = 0.5; // pixels per micrometer
        this.offsetX = 50;
        this.offsetY = 50;
        
        this.initializeEventListeners();
        this.drawGeometry();
    }
    
    initializeEventListeners() {
        // Control updates
        document.getElementById('line-type').addEventListener('change', () => this.updateGeometry());
        document.getElementById('trace-width').addEventListener('input', () => this.updateGeometry());
        document.getElementById('trace-height').addEventListener('input', () => this.updateGeometry());
        document.getElementById('substrate-height').addEventListener('input', () => this.updateGeometry());
        document.getElementById('substrate-width').addEventListener('input', () => this.updateGeometry());
        document.getElementById('substrate-er').addEventListener('input', () => this.updateEstimatedParams());
        document.getElementById('substrate-loss').addEventListener('input', () => this.updateEstimatedParams());
        document.getElementById('conductor-sigma').addEventListener('input', () => this.updateEstimatedParams());
        
        // Buttons
        document.getElementById('redraw-btn').addEventListener('click', () => this.drawGeometry());
        document.getElementById('export-btn').addEventListener('click', () => this.showExportModal());
        document.getElementById('clear-btn').addEventListener('click', () => this.clearCanvas());
        
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
    
    updateGeometry() {
        this.drawGeometry();
        this.updateEstimatedParams();
    }
    
    clearCanvas() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawGrid();
    }
    
    drawGrid() {
        const ctx = this.ctx;
        const gridSize = 50; // pixels
        
        ctx.strokeStyle = '#f0f0f0';
        ctx.lineWidth = 1;
        
        // Vertical lines
        for (let x = 0; x <= this.canvas.width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, this.canvas.height);
            ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= this.canvas.height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(this.canvas.width, y);
            ctx.stroke();
        }
    }
    
    drawGeometry() {
        // Clear canvas
        this.clearCanvas();
        
        // Get current parameters
        const params = this.getGeometryParams();
        
        // Convert dimensions to pixels
        const traceWidth = params.traceWidth * this.scale;
        const traceHeight = params.traceHeight * this.scale;
        const substrateWidth = params.substrateWidth * this.scale;
        const substrateHeight = params.substrateHeight * this.scale;
        
        // Calculate positions
        const canvasCenterX = this.canvas.width / 2;
        const substrateY = this.canvas.height - this.offsetY - substrateHeight;
        const substrateX = canvasCenterX - substrateWidth / 2;
        const traceX = canvasCenterX - traceWidth / 2;
        const traceY = substrateY - traceHeight;
        
        // Draw substrate
        this.ctx.fillStyle = '#27ae60'; // Green for substrate
        this.ctx.fillRect(substrateX, substrateY, substrateWidth, substrateHeight);
        this.ctx.strokeStyle = '#1e8449';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(substrateX, substrateY, substrateWidth, substrateHeight);
        
        // Draw trace based on transmission line type
        this.drawTrace(params.lineType, traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight);
        
        // Draw air/vacuum regions (after traces so it wraps around them)
        this.drawAirRegions(params.lineType, traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight);
        
        // Add dimensions annotations
        this.drawDimensions(traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight, params);
        
        // Add coordinate system
        this.drawCoordinateSystem();
    }
    
    drawTrace(lineType, traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight) {
        this.ctx.fillStyle = '#e67e22'; // Orange for conductor
        this.ctx.strokeStyle = '#d35400';
        this.ctx.lineWidth = 2;
        
        switch (lineType) {
            case 'microstrip':
                // Single trace on top of substrate
                this.ctx.fillRect(traceX, traceY, traceWidth, traceHeight);
                this.ctx.strokeRect(traceX, traceY, traceWidth, traceHeight);
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
                const gapWidth = 20; // pixels
                const groundWidth = 50; // pixels
                
                // Signal trace
                this.ctx.fillRect(traceX, traceY, traceWidth, traceHeight);
                this.ctx.strokeRect(traceX, traceY, traceWidth, traceHeight);
                
                // Left ground plane
                this.ctx.fillRect(traceX - gapWidth - groundWidth, traceY, groundWidth, traceHeight);
                this.ctx.strokeRect(traceX - gapWidth - groundWidth, traceY, groundWidth, traceHeight);
                
                // Right ground plane
                this.ctx.fillRect(traceX + traceWidth + gapWidth, traceY, groundWidth, traceHeight);
                this.ctx.strokeRect(traceX + traceWidth + gapWidth, traceY, groundWidth, traceHeight);
                break;
                
            case 'custom':
                // Basic trace for custom (user can extend this)
                this.ctx.fillRect(traceX, traceY, traceWidth, traceHeight);
                this.ctx.strokeRect(traceX, traceY, traceWidth, traceHeight);
                break;
        }
    }
    
    drawAirRegions(lineType, traceX, traceY, traceWidth, traceHeight, substrateX, substrateY, substrateWidth, substrateHeight) {
        this.ctx.fillStyle = '#ecf0f1'; // Light gray for air
        
        switch (lineType) {
            case 'microstrip':
                // Fill air above substrate and around the trace
                // Left side of trace
                this.ctx.fillRect(0, 0, traceX, substrateY);
                // Right side of trace
                this.ctx.fillRect(traceX + traceWidth, 0, this.canvas.width - (traceX + traceWidth), substrateY);
                // Above trace
                this.ctx.fillRect(traceX, 0, traceWidth, traceY);
                break;
                
            case 'stripline':
                // Stripline has top ground plane, so air is above it
                const topGroundY = substrateY - 20;
                this.ctx.fillRect(0, 0, this.canvas.width, topGroundY);
                break;
                
            case 'coplanar':
                // Trace with side ground planes - fill gaps and areas outside ground planes
                const gapWidth = 20; // pixels
                const groundWidth = 50; // pixels
                const leftGroundX = traceX - gapWidth - groundWidth;
                const rightGroundX = traceX + traceWidth + gapWidth + groundWidth;
                
                // Left of left ground plane
                this.ctx.fillRect(0, 0, leftGroundX, substrateY);
                // Right of right ground plane
                this.ctx.fillRect(rightGroundX, 0, this.canvas.width - rightGroundX, substrateY);
                // Gap between left ground and trace
                this.ctx.fillRect(traceX - gapWidth, 0, gapWidth, substrateY);
                // Gap between trace and right ground
                this.ctx.fillRect(traceX + traceWidth, 0, gapWidth, substrateY);
                // Above left ground plane
                this.ctx.fillRect(leftGroundX, 0, groundWidth, traceY);
                // Above trace
                this.ctx.fillRect(traceX, 0, traceWidth, traceY);
                // Above right ground plane
                this.ctx.fillRect(traceX + traceWidth + gapWidth, 0, groundWidth, traceY);
                break;
                
            case 'custom':
                // Custom - similar to microstrip, wrap around the trace
                // Left side of trace
                this.ctx.fillRect(0, 0, traceX, substrateY);
                // Right side of trace
                this.ctx.fillRect(traceX + traceWidth, 0, this.canvas.width - (traceX + traceWidth), substrateY);
                // Above trace
                this.ctx.fillRect(traceX, 0, traceWidth, traceY);
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
            substrateHeight: parseFloat(document.getElementById('substrate-height').value),
            substrateWidth: parseFloat(document.getElementById('substrate-width').value),
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
            
        } else {
            z0 = 50; // Default approximation
            effEr = params.substrateEr;
        }
        
        document.getElementById('z0-estimate').textContent = z0.toFixed(1) + ' Ω';
        document.getElementById('eff-er-estimate').textContent = effEr.toFixed(2);
    }
    
    showExportModal() {
        const params = this.getGeometryParams();
        const geometryData = {
            timestamp: new Date().toISOString(),
            transmissionLineType: params.lineType,
            dimensions: {
                traceWidth_um: params.traceWidth,
                traceHeight_um: params.traceHeight,
                substrateWidth_um: params.substrateWidth,
                substrateHeight_um: params.substrateHeight
            },
            materials: {
                substrate: {
                    relativePermittivity: params.substrateEr,
                    lossTangent: params.substrateLoss
                },
                conductor: {
                    conductivity_S_per_m: params.conductorSigma
                }
            },
            estimatedParameters: {
                characteristicImpedance_ohms: parseFloat(document.getElementById('z0-estimate').textContent),
                effectivePermittivity: parseFloat(document.getElementById('eff-er-estimate').textContent)
            }
        };
        
        document.getElementById('export-data').value = JSON.stringify(geometryData, null, 2);
        document.getElementById('export-modal').style.display = 'block';
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