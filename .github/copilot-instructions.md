# 2D EM Solver - GitHub Copilot Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Application Overview

The 2D EM Solver is a web-based transmission line geometry designer built with pure HTML5, CSS, and JavaScript. It allows users to create and configure 2D transmission line cross-sectional geometries for electromagnetic simulation. The application provides real-time impedance calculations, interactive parameter control, and JSON export functionality.

## Working Effectively

### Bootstrap and Run the Application
- Ensure Python 3 is available: `python3 --version`
- Start the HTTP server: `cd /home/runner/work/2D_EM_solver/2D_EM_solver && python3 -m http.server 8080`
- Navigate to `http://localhost:8080` in your browser
- **NO BUILD PROCESS REQUIRED** - This is a pure client-side web application

### Key Dependencies
- **Python 3**: Required only to serve the HTTP server for local development
- **Modern Web Browser**: Chrome 80+, Firefox 75+, Safari 13+, or Edge 80+ with HTML5 Canvas support
- **No package managers**: No npm, pip, or other package installation required

## Validation

### Manual Testing Scenarios
After making any changes, ALWAYS run through these validation scenarios:

1. **Basic Functionality Test**:
   - Start the HTTP server: `python3 -m http.server 8080`
   - Open `http://localhost:8080`
   - Verify the interface loads with default microstrip geometry
   - Confirm that the canvas displays the transmission line cross-section

2. **Parameter Validation Test**:
   - Change transmission line type from "Microstrip" to "Stripline"
   - Verify impedance value updates automatically (should change from ~138Ω to ~107Ω)
   - Modify trace width from 100μm to 150μm
   - Confirm the geometry redraws and impedance recalculates
   - Test all four transmission line types: Microstrip, Stripline, Coplanar Waveguide, Custom

3. **Export Functionality Test**:
   - Click "Export Geometry" button
   - Verify modal opens with properly formatted JSON data
   - Test "Copy to Clipboard" button (should work without errors)
   - Test "Download JSON" button (should trigger file download)
   - Close modal and verify application continues working

4. **Real-time Calculation Test**:
   - Change substrate εr from 4.4 to 2.2
   - Verify effective permittivity updates immediately
   - Modify trace dimensions and confirm impedance recalculates
   - Test material properties: loss tangent and conductor conductivity

### Browser Compatibility
- Test in at least one modern browser (Chrome, Firefox, Safari, or Edge)
- Verify HTML5 Canvas rendering works correctly
- Confirm all interactive controls are responsive

## File Structure and Key Components

### Core Files
- `index.html`: Main HTML interface with all UI controls and canvas element
- `styles.css`: Complete CSS styling including responsive design and modal styles  
- `geometry.js`: JavaScript implementation containing the `TransmissionLineGeometry` class with all functionality
- `README.md`: Project overview and quick start guide
- `UI_README.md`: Detailed UI documentation with usage instructions

### Key JavaScript Classes
- `TransmissionLineGeometry`: Main class handling all geometry rendering, calculations, and user interactions
  - Canvas drawing and grid rendering
  - Real-time impedance and effective permittivity calculations
  - Event handling for all UI controls
  - Export functionality (JSON generation, clipboard, download)

### Supported Transmission Line Types
- **Microstrip**: Single conductor above ground plane
- **Stripline**: Conductor between two ground planes  
- **Coplanar Waveguide**: Signal trace with ground planes on same layer
- **Custom**: Basic geometry for user customization

## Common Development Tasks

### Making Code Changes
- Edit HTML, CSS, or JavaScript files directly
- Refresh browser to see changes (no build step required)
- Test all affected functionality using validation scenarios above
- ALWAYS verify export functionality after JavaScript changes

### Adding New Features
- Follow existing code patterns in `geometry.js`
- Add new transmission line types by extending the `drawTrace()` method
- Update impedance calculations in `updateEstimatedParams()` method
- Test real-time updates and canvas rendering
- Ensure export JSON format remains compatible

### Debugging Issues
- Use browser developer tools (F12) to check console for JavaScript errors
- Verify canvas element exists and has proper dimensions (800x600)
- Check event listeners are properly bound in `initializeEventListeners()`
- Test HTTP server is serving files correctly

## Data Format

### JSON Export Structure
The application exports geometry data in this format:
```json
{
  "timestamp": "ISO_date_string",
  "transmissionLineType": "microstrip|stripline|coplanar|custom",
  "dimensions": {
    "traceWidth_um": number,
    "traceHeight_um": number,
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

## Timing Expectations

- **Application startup**: Instantaneous (pure HTML/CSS/JS)
- **HTTP server startup**: 1-2 seconds
- **Parameter updates**: Real-time (< 100ms)
- **Canvas rendering**: Near-instantaneous
- **Export operations**: < 1 second

## No Build/Test Infrastructure

This repository has:
- **No build system** (Make, npm, etc.)
- **No test framework** (Jest, Mocha, etc.)  
- **No linting tools** (ESLint, etc.)
- **No CI/CD pipelines**
- **No package.json or dependencies**

All validation must be done through manual testing in the browser.

## Future Development Notes

The repository structure indicates planned components:
- **2D EM Solver** (planned): Will process geometry data and calculate RLGC parameters
- **Slicer** (planned): Will extract cross-sections from KiCAD/Gerber layouts
- Current UI serves as the foundation for defining geometries manually

Always maintain compatibility with the current JSON export format to support future integration with the EM solver backend.