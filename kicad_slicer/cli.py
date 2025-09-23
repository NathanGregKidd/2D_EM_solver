"""
Command-line interface for the KiCad 2D EM Solver.
"""

import click
import sys
from pathlib import Path
from typing import Tuple

from .parser import parse_kicad_pcb
from .slicer import create_cross_section
from .visualizer import plot_cross_section, create_layer_stack_diagram


@click.group()
@click.version_option(version="0.1.0")
def main():
    """KiCad 2D EM Solver - Create cross-sections from KiCad PCB layouts."""
    pass


@main.command()
@click.argument('pcb_file', type=click.Path(exists=True, path_type=Path))
@click.option('--start', '-s', type=(float, float), required=True,
              help='Start point of slice line (x, y) in mm')
@click.option('--end', '-e', type=(float, float), required=True,
              help='End point of slice line (x, y) in mm')
@click.option('--width', '-w', type=float, default=0.1,
              help='Slice width tolerance in mm (default: 0.1)')
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output image file path (PNG or PDF)')
@click.option('--title', '-t', type=str, default="PCB Cross Section",
              help='Title for the cross-section plot')
@click.option('--no-nets', is_flag=True,
              help='Disable net color coding')
@click.option('--no-grid', is_flag=True,
              help='Disable grid lines')
@click.option('--figsize', type=(int, int), default=(12, 8),
              help='Figure size in inches (width, height)')
def slice(pcb_file: Path, start: Tuple[float, float], end: Tuple[float, float],
          width: float, output: Path, title: str, no_nets: bool, no_grid: bool,
          figsize: Tuple[int, int]):
    """Create a 2D cross-section from a KiCad PCB file."""
    
    try:
        # Parse the PCB file
        click.echo(f"Parsing KiCad PCB file: {pcb_file}")
        pcb_data = parse_kicad_pcb(str(pcb_file))
        
        # Create cross-section
        click.echo(f"Creating cross-section from ({start[0]:.2f}, {start[1]:.2f}) to ({end[0]:.2f}, {end[1]:.2f})")
        elements = create_cross_section(pcb_data, start, end, width)
        
        if not elements:
            click.echo("Warning: No elements found in the cross-section. "
                      "Try adjusting the slice line or increasing the slice width.", err=True)
        else:
            click.echo(f"Found {len(elements)} elements in cross-section")
        
        # Create visualization
        fig = plot_cross_section(
            elements,
            title=title,
            figsize=figsize,
            show_nets=not no_nets,
            show_grid=not no_grid,
            save_path=str(output) if output else None
        )
        
        if output:
            click.echo(f"Cross-section saved to: {output}")
        else:
            click.echo("Displaying cross-section...")
            fig.show()
            input("Press Enter to continue...")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('pcb_file', type=click.Path(exists=True, path_type=Path))
def info(pcb_file: Path):
    """Display information about a KiCad PCB file."""
    
    try:
        # Parse the PCB file
        click.echo(f"Parsing KiCad PCB file: {pcb_file}")
        pcb_data = parse_kicad_pcb(str(pcb_file))
        
        # Display information
        layers = pcb_data.get('layers', {})
        tracks = pcb_data.get('tracks', [])
        vias = pcb_data.get('vias', [])
        pads = pcb_data.get('pads', [])
        
        click.echo("\n=== PCB Information ===")
        click.echo(f"Layers: {len(layers)}")
        for name, layer in layers.items():
            click.echo(f"  - {name} (ID: {layer.id}, Type: {layer.type})")
        
        click.echo(f"\nTracks: {len(tracks)}")
        if tracks:
            layer_counts = {}
            for track in tracks:
                layer_counts[track.layer] = layer_counts.get(track.layer, 0) + 1
            for layer, count in sorted(layer_counts.items()):
                click.echo(f"  - {layer}: {count} tracks")
        
        click.echo(f"\nVias: {len(vias)}")
        click.echo(f"Pads: {len(pads)}")
        
        # Show nets
        all_nets = set()
        for track in tracks:
            if track.net > 0:
                all_nets.add(track.net)
        for via in vias:
            if via.net > 0:
                all_nets.add(via.net)
        for pad in pads:
            if pad.net > 0:
                all_nets.add(pad.net)
        
        click.echo(f"\nNets: {len(all_nets)}")
        if all_nets and len(all_nets) <= 20:  # Only show if not too many
            click.echo(f"  Net IDs: {sorted(all_nets)}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('pcb_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output image file path (PNG or PDF)')
@click.option('--figsize', type=(int, int), default=(8, 6),
              help='Figure size in inches (width, height)')
def layers(pcb_file: Path, output: Path, figsize: Tuple[int, int]):
    """Show the layer stack-up diagram for a KiCad PCB file."""
    
    try:
        # Parse the PCB file (we don't actually need the full data, just the concept)
        click.echo(f"Creating layer stack-up diagram for: {pcb_file}")
        
        # For now, use a standard 4-layer stack-up
        # In a full implementation, this would be extracted from the PCB file
        layer_stack = {
            'F.Cu': {'z_position': 1.5, 'thickness': 0.035, 'material': 'copper'},
            'Dielectric 1': {'z_position': 1.0, 'thickness': 1.0, 'material': 'fr4'},
            'In1.Cu': {'z_position': 0.5, 'thickness': 0.035, 'material': 'copper'},
            'Dielectric 2': {'z_position': 0.0, 'thickness': 1.0, 'material': 'fr4'},
            'In2.Cu': {'z_position': -0.5, 'thickness': 0.035, 'material': 'copper'},
            'Dielectric 3': {'z_position': -1.0, 'thickness': 1.0, 'material': 'fr4'},
            'B.Cu': {'z_position': -1.5, 'thickness': 0.035, 'material': 'copper'},
        }
        
        # Create visualization
        fig = create_layer_stack_diagram(layer_stack, figsize)
        
        if output:
            fig.savefig(str(output), dpi=300, bbox_inches='tight')
            click.echo(f"Layer stack-up diagram saved to: {output}")
        else:
            click.echo("Displaying layer stack-up diagram...")
            fig.show()
            input("Press Enter to continue...")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def examples():
    """Show usage examples."""
    
    click.echo("""
=== KiCad 2D EM Solver Examples ===

1. Get information about a PCB file:
   kicad-slicer info my_board.kicad_pcb

2. Create a cross-section from point (0,0) to (10,0):
   kicad-slicer slice my_board.kicad_pcb --start 0 0 --end 10 0

3. Create a cross-section and save it as PNG:
   kicad-slicer slice my_board.kicad_pcb -s 0 0 -e 10 0 -o cross_section.png

4. Create a cross-section with custom title and wider slice:
   kicad-slicer slice my_board.kicad_pcb -s 0 0 -e 10 0 -w 0.2 -t "My Cross Section"

5. Show layer stack-up diagram:
   kicad-slicer layers my_board.kicad_pcb

6. Create cross-section without net colors:
   kicad-slicer slice my_board.kicad_pcb -s 0 0 -e 10 0 --no-nets

=== Coordinate System ===
- Units are in millimeters (mm)
- Origin (0,0) is typically at the bottom-left of the PCB
- X-axis goes right, Y-axis goes up
- Z-axis (height) goes up from bottom copper layer

=== Tips ===
- Use 'info' command first to understand your PCB layout
- Start with a slice width of 0.1mm and adjust as needed
- For transmission lines, slice perpendicular to the trace
- Save results as PNG for sharing or PDF for high quality printing
    """)


if __name__ == '__main__':
    main()