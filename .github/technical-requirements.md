# Technical requirements
This document details the actual capabilities of the product.

## The Geometry Designer UI
The Geometry Designer UI provides the primary interface to the whole application. The user will spend most of the time here. Other user interfaces must be accessible from the Geometry Designer UI. The primary purpose of the Geometry Designer UI is to provide the user with the ability to construct a geometry to feed into the FEM solver backend.

### Capabilities (high level)
* Can build a custom geometry and export to backend
* Can open a dedicated UI for slicing a cross section of a 2.5D CAD layout (e.g. kicad layout or gerber)
* Can show basic rough estimates of transmission line parameters.

### User Requirements
* User must be able to export the created geometry to the FEM solver backend
* User must be able to use the Geometry Designer UI to design a geometry manually by specifying layers, elements, sizes, etc.
* User must be able to select from common types of planar transmission line geometries as presets
* User must be able to create a custom planar transmission line geometry 
* User must be able to see a rough estimate of the characteristic impedence of the chosen port
* User must be able to see a rough estimate of the effective relative permittivity of the chosen port
* User must be able to select which ports to calculate the transmission line parameters on.

### planar geometry creation
* Layers are vertically stacking, and are representative of layers in a PCB
* Layers may contain elements, representative of the physical things which exist on that layer.
* Elements may substrates, such as FR4, conductors, such as copper, empty space, such as air or vacuum. Vias also exist as an element.
* All layers shall conform to the same total outer dimension. In other words, if the bottom layer is 100mm wide, and the top layer only has a narrow conducter of 20mm wide, the rest of the space should be filled with a spacer of either air or vacuum such that the top layer has the same outer dimension as the largest outer dimension.
* Vias are able to be added in a layer, and span the height of a layer
* The width of a via can be specified
* The width and height of each element can be specified.
* The FEM solving parameters (such as conductivity, relative permittivity, etc) can be specified for each individual element
* Sizing parameters between two or more elements can be "linked" so that they have the same value. This allows adjusting multiple elements simultaneously and ensures that tracks are the same value if this is desired.
* Conductors can be specified as either ground or signal 1, signal 2, signal 3, etc.
* Ports can be specified as a collection of two conductors, one specified as reference and the other specified as the input.

### Current Implementation Details
* **Canvas Rendering**: 800x600 pixel canvas with 50-pixel grid system
* **Scaling Factor**: 0.5 pixels per micrometer for visualization
* **Color Coding**: Conductors (orange #ff6b35), substrate (green #4caf50), air (light gray #f0f0f0)
* **Real-time Updates**: Automatic recalculation triggered by input events
* **Default Values**: 
  - Trace width: 100 μm
  - Trace height: 35 μm  
  - Substrate height: 1600 μm
  - Substrate width: 2000 μm
  - Substrate εr: 4.4 (FR4)
  - Loss tangent: 0.02
  - Conductivity: 58000000 S/m (copper)

### Calculation Methods
* **Microstrip Impedance**: Wheeler's approximation formulas
* **Stripline Impedance**: Standard analytical formulas
* **Effective Permittivity**: Calculated using substrate and air interface effects
* **Estimation Accuracy**: Rough estimates for reference only, not for final design

## Solver backend
* The solver can accept the export format from the Geometry Designer UI
* The solver can be controlled from either the Geometry Designer UI or a dedicated GUI accessible from the Geometry Designer UI
* The solver uses FEM methods
* The solver meshes the given geometry
* The solver uses the mesh to solve maxwells equations numerically
* The solver uses the field solution to then solve for RLGC parameters of the transmission line
* The solver uses the exported geometry to decide what is a conductor and what is not
* The solver uses the exported geometry to decide what is the port of interest
* Ports may be defined as a signal source between two conductor. e.g. in microstrip it might be the single microstrip line and the ground plane. In differential pair the port could be *either* from one signal conductor to the other, or from one signal conductor to ground, or from both signal conductors to ground.
* The solver uses python or C and can be tested from the browser. Copilot should be able to test.

## System Requirements

### Platform Requirements
* **Operating Systems**: Cross-platform compatibility (Windows, macOS, Linux)
* **Python Version**: Python 3.8+ required for HTTP server and future backend solver
* **Web Browser Requirements**: 
  - Chrome 80+ (recommended)
  - Firefox 75+
  - Safari 13+
  - Edge 80+
  - HTML5 Canvas support mandatory
  - JavaScript ES6+ support required
* **Memory**: Minimum 4GB RAM for solver backend operations
* **Storage**: Minimum 100MB for application files and temporary data

### Performance Requirements
* **UI Responsiveness**: Parameter updates must complete within 100ms
* **Canvas Rendering**: Geometry updates must render within 50ms
* **Export Operations**: JSON export must complete within 1 second
* **File Size Limits**: Individual geometry files limited to 10MB
* **Concurrent Users**: System must support at least 10 concurrent users when deployed

## Data Format and Validation Requirements

### JSON Export Format Specifications
* **Timestamp Format**: ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ)
* **Dimensional Units**: All dimensions must be in micrometers (μm)
* **Material Property Ranges**:
  - Relative permittivity (εr): 1.0 to 100.0
  - Loss tangent: 0.0 to 1.0
  - Conductivity: 1e3 to 1e8 S/m
* **Geometry Validation**: All dimensional values must be positive numbers
* **File Naming Convention**: `transmission_line_geometry_YYYY-MM-DDTHH-mm-ss.json`

### Extended Transmission Line Types Support
* **Current Implementation**: Microstrip, Stripline, Coplanar Waveguide, Custom
* **Planned Extensions**:
  - Coplanar Waveguide with Ground
  - Grounded Coplanar Waveguide  
  - Differential Pair
  - Differential Coplanar Waveguide
  - Differential Coplanar Waveguide with Ground
  - Grounded Differential Coplanar Waveguide

## User Interface Requirements

### Accessibility Requirements
* **Keyboard Navigation**: All controls must be accessible via keyboard
* **Screen Reader Support**: Labels and descriptions for all form elements
* **Color Contrast**: Minimum WCAG 2.1 AA compliance (4.5:1 ratio)
* **Font Size**: Minimum 14px for body text, scalable to 200%
* **Focus Indicators**: Clear visual focus indicators for all interactive elements

### Responsive Design Requirements
* **Mobile Support**: Functional on devices with minimum 320px width
* **Tablet Support**: Optimized layout for tablet devices (768px+)
* **Desktop Support**: Full feature support on desktop (1200px+)
* **Canvas Scaling**: Automatic canvas scaling on smaller screens
* **Touch Support**: Touch-friendly controls for mobile/tablet devices

## Security Requirements

### Client-Side Security
* **Input Validation**: All user inputs must be validated and sanitized
* **XSS Prevention**: Protection against cross-site scripting attacks
* **File Upload Restrictions**: Validate file types and sizes for future import features
* **Local Storage**: Secure handling of any locally stored data

### Data Privacy
* **No Server Communication**: Current UI operates entirely client-side
* **Local Processing**: All calculations performed locally in browser
* **Export Control**: User has full control over data export and sharing

## Integration Requirements

### Backend Solver Integration
* **Communication Protocol**: RESTful API or WebSocket connection to Python solver
* **Data Exchange Format**: JSON format compatible with current export structure
* **Error Handling**: Graceful handling of solver errors and timeouts
* **Progress Reporting**: Real-time progress updates during FEM calculations

### Slicer Component Integration
* **File Format Support**: Gerber files, KiCad layouts, and other PCB formats
* **Cross-section Export**: Direct integration with geometry designer
* **Coordinate System**: Consistent coordinate mapping between slicer and designer

### Future CAD Integration
* **Import Formats**: Support for common CAD file formats
* **Export Formats**: Compatibility with industry-standard EM simulation tools
* **API Endpoints**: RESTful API for programmatic access

## Testing and Validation Requirements

### Automated Testing
* **Unit Tests**: Coverage for all calculation functions
* **Integration Tests**: End-to-end testing of export/import workflows
* **Cross-browser Testing**: Validation across all supported browsers
* **Performance Testing**: Automated performance benchmarking

### Manual Testing Requirements
* **Geometry Validation**: Visual verification of drawn geometries
* **Parameter Accuracy**: Validation of impedance calculations against known values
* **Export Functionality**: Verification of JSON format and data integrity
* **User Workflow Testing**: Complete user journey validation

## Deployment Requirements

### Development Environment
* **No Build Process**: Pure client-side application with no compilation step
* **Local Server**: Python 3 HTTP server for development
* **Hot Reload**: Immediate reflection of code changes (browser refresh)

### Production Deployment
* **Static Hosting**: Compatible with static web hosting services
* **CDN Support**: Optimized for content delivery networks
* **HTTPS Required**: Secure connection mandatory for production use
* **Caching Strategy**: Appropriate cache headers for static assets

### Documentation Requirements
* **Technical Documentation**: Complete API documentation for all components
* **User Guide**: Comprehensive user manual with examples
* **Developer Guide**: Setup and contribution guidelines
* **Change Log**: Detailed version history and breaking changes

## Error Handling and Robustness Requirements

### Input Validation
* **Numerical Inputs**: All dimensional and material property inputs must be validated for positive values
* **Range Checking**: Material properties must be within physically reasonable ranges
* **Error Messages**: Clear, user-friendly error messages for invalid inputs
* **Graceful Degradation**: Application continues to function with default values when inputs are invalid

### Application Stability
* **Memory Management**: Proper cleanup of canvas contexts and event listeners
* **Browser Compatibility**: Fallback mechanisms for unsupported browser features
* **Performance Monitoring**: Detection and handling of performance issues
* **State Recovery**: Ability to recover from corrupted application state

### Data Integrity
* **Export Validation**: JSON export format validation before download/copy
* **Import Validation**: Future import functionality must validate data structure
* **Backup Mechanisms**: Local storage backup of user configurations
* **Version Compatibility**: Forward and backward compatibility for data formats
