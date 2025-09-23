#!/usr/bin/env python3
"""
Demo script showing KiCad 2D EM Solver capabilities.
"""

from kicad_slicer.parser import parse_kicad_pcb
from kicad_slicer.slicer import create_cross_section
from kicad_slicer.visualizer import plot_cross_section


def main():
    """Run the demo."""
    print("KiCad 2D EM Solver Demo")
    print("=" * 50)
    
    # Parse the example PCB file
    pcb_file = "examples/test_board.kicad_pcb"
    print(f"Parsing PCB file: {pcb_file}")
    
    pcb_data = parse_kicad_pcb(pcb_file)
    
    # Display basic information
    print(f"Found {len(pcb_data['layers'])} layers")
    print(f"Found {len(pcb_data['tracks'])} tracks")
    print(f"Found {len(pcb_data['vias'])} vias")
    print(f"Found {len(pcb_data['pads'])} pads")
    
    # Create a horizontal cross-section
    print("\nCreating horizontal cross-section...")
    elements_h = create_cross_section(
        pcb_data,
        start_point=(0, 10),
        end_point=(30, 10),
        slice_width=0.2
    )
    
    print(f"Cross-section contains {len(elements_h)} elements:")
    for i, elem in enumerate(elements_h):
        print(f"  {i+1}. {elem.element_type} on {elem.layer_name} "
              f"({elem.x_start:.1f}-{elem.x_end:.1f}mm, "
              f"{elem.z_start:.1f}-{elem.z_end:.1f}mm)")
    
    # Create visualization
    fig_h = plot_cross_section(
        elements_h,
        title="Horizontal Cross-Section (y=10mm)",
        save_path="demo_horizontal.png"
    )
    print("Horizontal cross-section saved to: demo_horizontal.png")
    
    # Create a vertical cross-section through a via
    print("\nCreating vertical cross-section through via...")
    elements_v = create_cross_section(
        pcb_data,
        start_point=(15, 0),
        end_point=(15, 15),
        slice_width=0.2
    )
    
    fig_v = plot_cross_section(
        elements_v,
        title="Vertical Cross-Section Through Via (x=15mm)",
        save_path="demo_vertical.png"
    )
    print("Vertical cross-section saved to: demo_vertical.png")
    
    print("\nDemo complete! Check the generated PNG files.")


if __name__ == "__main__":
    main()