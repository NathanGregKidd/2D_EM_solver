# 2D Transmission Line Geometry Designer

## Overview

This web-based UI allows users to create and configure 2D transmission line cross-sectional geometries for electromagnetic simulation. The application is designed to work with the 2D EM solver and provides an intuitive interface for defining transmission line parameters.

## Features

### Supported Transmission Line Types
- **Microstrip**: Single trace on substrate with ground plane below
- **Stripline**: Trace embedded between ground planes
- **Coplanar Waveguide**: Trace with side ground planes on same layer  
- **Coplanar Waveguide with Ground**: Coplanar waveguide with additional ground plane below substrate
- **Grounded Coplanar Waveguide**: Coplanar waveguide with ground plane below and vias connecting coplanar grounds to bottom ground
- **Custom**: User-defined configuration for special cases

### Geometry Controls
- **Dimensions**: Configure trace width, height, ground plane thickness, coplanar gap width, substrate dimensions (in micrometers)
- **Materials**: Set substrate dielectric constant (εr), loss tangent, and conductor properties
- **Real-time Updates**: Geometry visualization and parameter estimation update automatically

### Visualization
- **Cross-section View**: Canvas-based rendering of the transmission line geometry
- **Color-coded Materials**: Signal conductor (orange), ground plane (brown), vias (gray), substrate (green), air (light gray)
- **Dimensional Annotations**: Key measurements displayed on the geometry
- **Grid Background**: Reference grid for scale
- **Zoom and Pan**: Interactive controls for viewing geometry at any scale
  - **Mouse Wheel Zoom**: Scroll to zoom in/out (zooms towards cursor position)
  - **Click and Drag**: Pan the view by clicking and dragging on the canvas
  - **Zoom Buttons**: +/− buttons for precise zoom control (10% to 1000% range)
  - **Reset View**: ⟲ button to return to default view
  - **Zoom Display**: Current zoom level shown as percentage

### Parameter Estimation
- **Characteristic Impedance (Z₀)**: Approximate values using standard formulas
- **Effective Permittivity (εₑff)**: Calculated effective dielectric constant
- **Real-time Calculation**: Updates automatically when parameters change

### Export Functionality
- **JSON Export**: Complete geometry and material data in structured format
- **Copy to Clipboard**: Quick data sharing capability
- **Download File**: Save geometry data as JSON file with timestamp

## Usage

1. **Select Transmission Line Type**: Choose from microstrip, stripline, coplanar, or custom
2. **Set Dimensions**: Enter trace width, height, and substrate dimensions in micrometers
3. **Configure Materials**: Set dielectric constant, loss tangent, and conductivity
4. **View Geometry**: The canvas automatically displays the cross-sectional view
5. **Zoom and Pan**: Use mouse wheel to zoom, or click zoom buttons; click and drag to pan
6. **Check Parameters**: Review estimated impedance and effective permittivity
7. **Export Data**: Use the export button to save or copy the geometry data

## Technical Details

### File Structure
- `index.html`: Main HTML interface
- `styles.css`: CSS styling and responsive design
- `geometry.js`: JavaScript implementation with geometry rendering and calculations

### Impedance Calculations
- **Microstrip**: Wheeler's formulas for characteristic impedance
- **Stripline**: Standard stripline impedance formulas
- **Real-time Updates**: Calculations update as parameters change

### Data Format
Exported geometry data includes:
```json
{
  "timestamp": "ISO_date_string",
  "transmissionLineType": "microstrip|stripline|coplanar|custom",
  "dimensions": {
    "traceWidth_um": number,
    "traceHeight_um": number,
    "groundThickness_um": number,
    "coplanarGap_um": number,
    "substrateWidth_um": number,
    "substrateHeight_um": number
  },
  "materials": {
    "substrate": {
      "relativePermittivity": number,
      "lossTangent": number
    },
    "conductor": {
      "conductivity_S_per_m": number
    }
  },
  "estimatedParameters": {
    "characteristicImpedance_ohms": number,
    "effectivePermittivity": number
  }
}
```

## Browser Compatibility

The application works in modern web browsers with HTML5 Canvas support:
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Getting Started

1. Clone the repository
2. Open `index.html` in a web browser, or serve via HTTP server:
   ```bash
   python3 -m http.server 8080
   ```
3. Navigate to `http://localhost:8080`

## Future Enhancements

- Additional transmission line types (differential pairs, via transitions)
- Advanced material models (frequency-dependent properties)
- 3D visualization capabilities
- Integration with EM solver backend
- Batch geometry processing
- Import from CAD formats