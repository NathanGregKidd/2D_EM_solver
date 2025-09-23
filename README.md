# 2D_EM_solver
A 2D EM solver able to slice KiCAD and other layout types and give you EM data on the sliced area.

# Current Status
✅ **2D Transmission Line Geometry Designer UI** - Complete and functional web-based interface for creating transmission line geometries.

# Components

## 2D Transmission Line Geometry Designer (✅ Implemented)
A web-based UI that allows users to create and configure 2D transmission line cross-sectional geometries. Features include:

- **Multiple transmission line types**: Microstrip, Stripline, Coplanar Waveguide, and Custom
- **Interactive parameter control**: Real-time geometry updates and impedance calculations
- **Material property configuration**: Substrate permittivity, loss tangent, conductor properties
- **Visual geometry rendering**: Canvas-based cross-sectional view with dimensional annotations
- **Data export**: JSON export functionality for geometry and material data
- **Parameter estimation**: Automatic calculation of characteristic impedance and effective permittivity

### Quick Start
```bash
# Serve the UI locally
python3 -m http.server 8080
# Open http://localhost:8080 in your browser
```

See [UI_README.md](UI_README.md) for detailed documentation.

## 2D EM Solver (🔄 Planned)
The solver will work a lot like Polar si9000 transmission line field solver. The inputs are a two dimensional geometry describing the transmission line (which is almost always a PCB microstrip or stripline or otherwise planar geometry). The output of this program will be RLGC parameters, characteristic impedence, and other transmission line parameters.

## Slicer (🔄 Planned)
The slicer will allow the user to "draw a line" across a portion of a layout. The layout will be in a gerber format or something similar, as in a top-down 2.5D layout. By "drawing a line", that line will slice through the layout and the cross section of that line through the layout will be displayed. The point of this is so that a cross section of a transmission line can be obtained. This way, the user can just draw a line through the transmission line in question and obtain a 2D cross sectional geometry. This geometry will be then fed into the 2D EM solver.

# Goal
The ultimate goal is that users can have a 2.5D layout from KiCAD or gerbers etc, and make a cross section at will. This cross section will automatically be solved for transmission line parameters. The current UI provides the foundation for defining these geometries manually.
