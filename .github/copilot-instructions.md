# 2D EM Solver - GitHub Copilot Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

In addition, always check the technical-requirements.md document when making preperations. 

## Application Overview

The 2D EM Solver consists of a JavaScript-based frontend UI (Geometry Designer) and a planned Python-based FEM backend. The frontend allows users to create and configure 2D transmission line cross-sectional geometries with rough transmission line parameter estimations for reference only. Once the geometry is finalized, it exports to a more rigorous Python backend based on FEM analysis that solves Maxwell's equations for accurate solutions. The current UI provides real-time impedance calculations, interactive parameter control, and JSON export functionality.

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
   - Test all transmission line types: Microstrip, Stripline, Coplanar Waveguide, Coplanar Waveguide with Ground, Grounded Coplanar Waveguide, Differential Pair, Differential Coplanar Waveguide, Differential Coplanar Waveguide with Ground, Grounded Differential Coplanar Waveguide, Custom

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
- **Coplanar Waveguide with Ground**: Coplanar waveguide with additional ground plane
- **Grounded Coplanar Waveguide**: Coplanar waveguide with ground plane beneath
- **Differential Pair**: Two signal conductors for differential signaling
- **Differential Coplanar Waveguide**: Differential pair with coplanar ground planes
- **Differential Coplanar Waveguide with Ground**: Differential coplanar with additional ground plane
- **Grounded Differential Coplanar Waveguide**: Differential coplanar with ground plane beneath
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
- Update impedance calculations in `updateEstimatedParams()` method (these are rough estimates for reference only)
- Test real-time updates and canvas rendering
- The JSON export format is still evolving and may change as the system develops

### Debugging Issues
- Use browser developer tools (F12) to check console for JavaScript errors
- Verify canvas element exists and has proper dimensions (800x600)
- Check event listeners are properly bound in `initializeEventListeners()`
- Test HTTP server is serving files correctly

## Data Format

### JSON Export Structure
The application will export geometry data with support for layers, conductors, substrates, and spacers. The planned format structure:
```json
{
  "timestamp": "ISO_date_string",
  "transmissionLineType": "microstrip|stripline|coplanar|custom",
  "layers": [
    {
      "layerNumber": 1,
      "elements": [
        {
          "type": "conductor",
          "conductorType": "ground",
          "conductorParameters": {},
          "sizeParameters": {}
        }
      ]
    },
    {
      "layerNumber": 2,
      "elements": [
        {
          "type": "substrate",
          "substrateType": "FR4",
          "sizeParameters": {}
        }
      ]
    },
    {
      "layerNumber": 3,
      "elements": [
        {
          "type": "spacer",
          "spacerType": "air",
          "sizeParameters": {}
        },
        {
          "type": "conductor",
          "conductorType": "signal1",
          "conductorParameters": {},
          "sizeParameters": {}
        },
        {
          "type": "spacer",
          "spacerType": "air",
          "sizeParameters": {}
        }
      ]
    }
  ]
}
```
Note: Layers are interpreted from bottom to top (layer 1 is bottom, layer 3 is top). Elements within layers are interpreted from left to right.

## Timing Expectations

- **Application startup**: Instantaneous (pure HTML/CSS/JS)
- **HTTP server startup**: 1-2 seconds
- **Parameter updates**: Real-time (< 100ms)
- **Canvas rendering**: Near-instantaneous
- **Export operations**: < 1 second

## Build/Test Infrastructure

### Current State
This repository currently has:
- **No build system** (Make, npm, etc.)
- **No test framework** (Jest, Mocha, etc.)  
- **No linting tools** (ESLint, etc.)
- **No CI/CD pipelines**
- **No package.json or dependencies**

All validation must be done through manual testing in the browser.

### Future State
Once the FEM system is implemented in Python, there may or may not be a build system. The Python FEM backend will likely require its own dependencies and setup procedures.

## Future Development Notes

The repository structure indicates planned components:
- **2D EM Solver** (planned): Will process geometry data and calculate RLGC parameters through FEM numerical methods solving Maxwell's equations
- **Slicer** (planned): Will extract cross-sections from KiCAD/Gerber layouts
- Current UI serves as the foundation for defining geometries manually

The JSON export format is not yet finalized and may change as the system evolves. Backward compatibility is not currently a priority until a working system is established.

# GitHub Copilot Instructions

- Always use the `Dev` branch as the base for all pull requests, unless explicitly instructed otherwise.
- Reference files, code, and context from the `Dev` branch when generating code, documentation, or answering questions.
- Avoid using the `main` branch for PRs or code references unless specifically requested.
