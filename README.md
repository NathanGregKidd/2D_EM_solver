# KiCad 2D EM Solver

A 2D EM solver able to slice KiCAD layouts and create cross-sections for transmission line analysis.

## Features

- **KiCad Parser**: Reads and parses .kicad_pcb files in S-expression format
- **Cross-Section Slicer**: Creates 2D cross-sections along user-defined lines through PCB layouts
- **Visualization**: Generates clear diagrams of cross-sections with material and net identification
- **Command-Line Interface**: Easy-to-use CLI for batch processing and automation
- **Layer Stack-up**: Handles multi-layer PCB structures with proper Z-positioning

## Installation

```bash
# Clone the repository
git clone https://github.com/NathanGregKidd/2D_EM_solver.git
cd 2D_EM_solver

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

### 1. Get PCB Information
```bash
kicad-slicer info examples/test_board.kicad_pcb
```

### 2. Create a Cross-Section
```bash
# Create a horizontal cross-section at y=10mm
kicad-slicer slice examples/test_board.kicad_pcb --start 0 10 --end 30 10

# Save the cross-section as PNG
kicad-slicer slice examples/test_board.kicad_pcb -s 0 10 -e 30 10 -o cross_section.png
```

### 3. View Layer Stack-up
```bash
kicad-slicer layers examples/test_board.kicad_pcb
```

## Usage Examples

### Command Line Interface

The main interface is through the `kicad-slicer` command:

```bash
# Show all available commands
kicad-slicer --help

# Show usage examples
kicad-slicer examples

# Get detailed information about a PCB
kicad-slicer info my_board.kicad_pcb

# Create cross-section with custom parameters
kicad-slicer slice my_board.kicad_pcb \
  --start 5.0 10.0 \
  --end 25.0 10.0 \
  --width 0.2 \
  --title "Transmission Line Cross-Section" \
  --output transmission_line.png
```

### Python API

You can also use the library programmatically:

```python
from kicad_slicer.parser import parse_kicad_pcb
from kicad_slicer.slicer import create_cross_section
from kicad_slicer.visualizer import plot_cross_section

# Parse KiCad file
pcb_data = parse_kicad_pcb("my_board.kicad_pcb")

# Create cross-section
elements = create_cross_section(
    pcb_data, 
    start_point=(0, 10),
    end_point=(30, 10),
    slice_width=0.1
)

# Visualize
fig = plot_cross_section(elements, title="My Cross Section")
fig.show()
```

## Architecture

### Components

1. **Parser Module** (`parser.py`)
   - Handles S-expression parsing of KiCad files
   - Extracts tracks, vias, pads, and layer information
   - Provides data structures for PCB elements

2. **Slicer Module** (`slicer.py`) 
   - Creates 2D cross-sections along specified lines
   - Handles geometric intersections and projections
   - Manages layer stack-up and Z-positioning

3. **Visualizer Module** (`visualizer.py`)
   - Generates matplotlib plots of cross-sections
   - Color-codes materials and nets
   - Creates layer stack-up diagrams

4. **CLI Module** (`cli.py`)
   - Provides command-line interface
   - Handles file I/O and user interaction

### Data Flow

```
KiCad File → Parser → PCB Data → Slicer → Cross-Section Elements → Visualizer → Plot
```

## Supported Features

### KiCad Elements
- ✅ Tracks (segments)
- ✅ Vias  
- ✅ Pads
- ✅ Layer definitions
- ✅ Net information

### PCB Structures
- ✅ Multi-layer boards (4-layer stack-up)
- ✅ Copper layers
- ✅ Dielectric layers (FR4)
- ✅ Via connections between layers

### Visualization
- ✅ Material color coding
- ✅ Net identification
- ✅ Layer labels
- ✅ Dimensional accuracy
- ✅ Export to PNG/PDF

## Future Goals

### 2D EM Solver Integration
The current implementation provides the foundation for 2D EM solving:
- Cross-sections can be exported as geometry data
- Material properties are identified
- Layer stack-up information is preserved

Future development will add:
- RLGC parameter calculation
- Characteristic impedance computation
- Field distribution visualization
- Frequency-dependent analysis

### Enhanced Features
- Support for more KiCad elements (polygons, text, etc.)
- Gerber file parsing
- Custom material properties
- Interactive cross-section selection
- 3D visualization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## Testing

```bash
# Run basic tests
python -m pytest tests/

# Run specific test
python tests/test_basic.py
```

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.
