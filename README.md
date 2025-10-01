# 2D Electromagnetic Field Solver

A Python-based 2D electromagnetic field solver for transmission line analysis. This solver computes RLGC parameters, characteristic impedance, and other transmission line parameters from 2D cross-sectional geometries.

## Features

- **2D Field Solver**: Finite element method for solving Laplace's, Poisson's, and Helmholtz' equation with dielectric materials
- **Transmission Line Analysis**: Calculate RLGC parameters and characteristic impedance
- **Predefined Geometries**: Built-in support for microstrip, stripline, coplanar waveguide configurations
- **Field Visualization**: Plot electric potential and field distributions
- **Analytical Validation**: Compare results with analytical formulas
- **Command Line Interface**: Easy-to-use CLI for common analyses
- **Frequency Analysis**: Frequency sweep capabilities
- **Multiple transmission line types**: Microstrip, Stripline, Coplanar Waveguide, and Custom
- **Interactive parameter control**: Real-time geometry updates and impedance calculations
- **Zoom and pan controls**: Mouse wheel zoom, click-drag pan, and zoom buttons for exploring geometries at any scale
- **Material property configuration**: Substrate permittivity, loss tangent, conductor properties
- **Visual geometry rendering**: Canvas-based cross-sectional view with dimensional annotations
- **Data export**: JSON export functionality for geometry and material data
- **Parameter estimation**: Automatic calculation of characteristic impedance and effective permittivity

## Installation


### Prerequisites
- Python 3.8 or higher
- NumPy, SciPy, Matplotlib

### Install from source
```bash
git clone https://github.com/NathanGregKidd/2D_EM_solver.git
cd 2D_EM_solver
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Command Line Interface

Analyze a microstrip transmission line:
```bash
2d-em-solver microstrip --width 0.005 --height 0.0016 --trace-width 0.003 --trace-thickness 0.000035 --er 4.6
```

Analyze a stripline with plots:
```bash
2d-em-solver stripline --width 0.004 --height 0.002 --trace-width 0.0008 --trace-thickness 0.000035 --save-plots
```

### Python API

```python
from em_solver.geometry import create_microstrip_geometry
from em_solver.solver import FieldSolver2D, SolverParameters
from em_solver.transmission_line import calculate_transmission_line_parameters

# Create microstrip geometry
geometry = create_microstrip_geometry(
    substrate_width=0.005,     # 5mm
    substrate_height=0.0016,   # 1.6mm FR4
    trace_width=0.003,        # 3mm trace
    trace_thickness=0.000035, # 35μm copper
    substrate_er=4.6          # FR4 dielectric
)

# Setup solver parameters
params = SolverParameters(nx=100, ny=100, frequency=1e9)

# Calculate transmission line parameters
tl_params = calculate_transmission_line_parameters(
    geometry=geometry,
    parameters=params,
    frequency=1e9
)

print(f"Characteristic Impedance: {tl_params.Z0:.1f} Ω")
print(f"Effective Permittivity: {tl_params.epsilon_eff:.2f}")
```

## Examples

Run the comprehensive example script:
```bash
python examples/example_usage.py
```

This demonstrates:
- Microstrip analysis with field visualization
- Stripline analysis
- Frequency sweep analysis
- Comparison with analytical formulas

## Theory

The solver uses the finite difference method to solve the 2D electrostatic problem:

∇ · (ε ∇V) = 0

Where:
- V is the electric potential
- ε is the permittivity distribution

The transmission line parameters are calculated from the field solution:
- **Capacitance (C)**: From the capacitance matrix using multiple voltage excitations
- **Inductance (L)**: Using the relationship L = μ₀ε₀ × C_air / C
- **Resistance (R)**: From skin effect in conductors
- **Conductance (G)**: From dielectric losses
- **Characteristic Impedance (Z₀)**: Z₀ = √(Z/Y) where Z = R + jωL, Y = G + jωC

## Supported Geometries

### Microstrip
- Signal trace above a ground plane
- Dielectric substrate (e.g., FR4)
- Air above the trace

### Stripline  
- Signal trace between two ground planes
- Symmetric or asymmetric configurations
- Homogeneous dielectric environment

### Custom Geometries
The flexible geometry system allows defining arbitrary rectangular regions with different materials.

## Validation

The solver is validated against analytical formulas:

| Geometry | Formula | Typical Accuracy |
|----------|---------|------------------|
| Microstrip | Wheeler's approximation | ±10% |
| Stripline | IPC-2141 formulas | ±5% |

## API Reference

### Core Classes

- `Geometry2D`: 2D cross-section definition
- `Material`: Material properties (εᵣ, σ, μᵣ)
- `FieldSolver2D`: Main electromagnetic solver
- `SolverParameters`: Solver configuration
- `TransmissionLineParameters`: Complete RLGC results

### Key Functions

- `create_microstrip_geometry()`: Create microstrip geometry
- `create_stripline_geometry()`: Create stripline geometry
- `calculate_transmission_line_parameters()`: Main analysis function
- `calculate_characteristic_impedance_analytical()`: Analytical formulas

## Future Enhancements

The current implementation provides a solid foundation for 2D field analysis. Future enhancements could include:

### Slicer Component
- **Layout Import**: Support for KiCAD, Gerber, and other PCB layout formats  
- **Cross-Section Generation**: Interactive line drawing to create 2D slices
- **3D to 2D Conversion**: Automatic generation of 2D geometries from 3D layouts
- **Stackup Integration**: Multi-layer PCB stackup support

### Advanced Features
- **Non-rectangular Geometries**: Curved and angled conductor shapes
- **Multi-layer Analysis**: Via stitching and layer transitions
- **Differential Pairs**: Coupled transmission line analysis
- **Dispersion Analysis**: Frequency-dependent parameters
- **Loss Modeling**: More sophisticated conductor and dielectric loss models

## Contributing

Contributions are welcome! Please see the development guidelines for more information.

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.