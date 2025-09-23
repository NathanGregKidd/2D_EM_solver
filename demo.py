"""Demonstration of the 2D EM solver functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import matplotlib.pyplot as plt

from em_solver.geometry import create_microstrip_geometry, create_stripline_geometry
from em_solver.solver import FieldSolver2D, SolverParameters
from em_solver.transmission_line import (
    calculate_transmission_line_parameters,
    calculate_characteristic_impedance_analytical
)
from em_solver.visualization import create_complete_field_plot

def demonstrate_microstrip():
    """Demonstrate microstrip analysis with realistic parameters."""
    print("="*60)
    print("MICROSTRIP TRANSMISSION LINE DEMONSTRATION")
    print("="*60)
    
    # Create realistic microstrip geometry
    # Using thicker trace for better numerical stability
    geometry = create_microstrip_geometry(
        substrate_width=0.008,    # 8mm wide substrate (plenty of margin)
        substrate_height=0.0016,  # 1.6mm FR4 substrate  
        trace_width=0.003,       # 3mm trace width
        trace_thickness=0.0003,   # 300μm thick (for numerical stability)
        substrate_er=4.6,         # FR4 dielectric constant
        conductor_name="signal"
    )
    
    print("Geometry created:")
    print(f"  Substrate: 8.0 × 1.6 mm (εᵣ = 4.6)")
    print(f"  Trace: 3.0 × 0.3 mm")
    print(f"  Regions: {len(geometry.regions)}")
    print(f"  Conductors: {len(geometry.get_conductor_regions())}")
    
    # Solver with good resolution
    params = SolverParameters(nx=80, ny=80, frequency=1e9)
    
    print(f"\nSolver setup:")
    print(f"  Grid: {params.nx} × {params.ny}")
    print(f"  Frequency: 1.0 GHz")
    
    # Calculate transmission line parameters
    print("\nSolving electromagnetic field problem...")
    tl_params = calculate_transmission_line_parameters(
        geometry=geometry,
        parameters=params,
        frequency=1e9,
        conductor_names=("signal", "ground")
    )
    
    # Calculate analytical result for comparison
    z0_analytical = calculate_characteristic_impedance_analytical(
        "microstrip",
        trace_width=0.003,
        substrate_height=0.0016,
        epsilon_r=4.6
    )
    
    print(f"\nResults:")
    print(f"  Numerical Z₀: {tl_params.Z0:.1f} Ω")
    print(f"  Analytical Z₀: {z0_analytical:.1f} Ω")
    print(f"  Relative Error: {abs(tl_params.Z0 - z0_analytical)/z0_analytical*100:.1f}%")
    print(f"  Capacitance: {tl_params.C*1e12:.1f} pF/m")
    print(f"  Inductance: {tl_params.L*1e9:.1f} nH/m")
    print(f"  Effective εᵣ: {tl_params.epsilon_eff:.2f}")
    
    # Create field visualization
    print("\nGenerating field visualization...")
    solver = FieldSolver2D(geometry, params)
    solution = solver.solve_electrostatic({"signal": 1.0, "ground": 0.0})
    
    fig = create_complete_field_plot(solution)
    fig.suptitle(f"Microstrip Line (Z₀ = {tl_params.Z0:.1f} Ω)", fontsize=14)
    plt.savefig("microstrip_demo.png", dpi=150, bbox_inches='tight')
    print("Field plot saved as: microstrip_demo.png")
    
    return tl_params, solution


def demonstrate_stripline():
    """Demonstrate stripline analysis."""
    print("\n" + "="*60)
    print("STRIPLINE TRANSMISSION LINE DEMONSTRATION") 
    print("="*60)
    
    # Create stripline geometry
    geometry = create_stripline_geometry(
        substrate_width=0.006,    # 6mm wide
        substrate_height=0.004,   # 4mm between ground planes
        trace_width=0.002,       # 2mm trace width
        trace_thickness=0.0003,   # 300μm thick
        substrate_er=4.2,         # Low loss dielectric
        conductor_name="signal"
    )
    
    print("Geometry created:")
    print(f"  Substrate: 6.0 × 4.0 mm (εᵣ = 4.2)")
    print(f"  Trace: 2.0 × 0.3 mm (centered)")
    
    # Solver setup
    params = SolverParameters(nx=60, ny=60, frequency=2e9)  # 2 GHz
    
    print(f"\nSolver setup:")
    print(f"  Grid: {params.nx} × {params.ny}")
    print(f"  Frequency: 2.0 GHz")
    
    # Calculate transmission line parameters
    print("\nSolving electromagnetic field problem...")
    tl_params = calculate_transmission_line_parameters(
        geometry=geometry,
        parameters=params,
        frequency=2e9,
        conductor_names=("signal", "ground")
    )
    
    # Analytical comparison
    z0_analytical = calculate_characteristic_impedance_analytical(
        "stripline",
        trace_width=0.002,
        substrate_height=0.004,
        epsilon_r=4.2
    )
    
    print(f"\nResults:")
    print(f"  Numerical Z₀: {tl_params.Z0:.1f} Ω")
    print(f"  Analytical Z₀: {z0_analytical:.1f} Ω")  
    print(f"  Relative Error: {abs(tl_params.Z0 - z0_analytical)/z0_analytical*100:.1f}%")
    print(f"  Capacitance: {tl_params.C*1e12:.1f} pF/m")
    print(f"  Inductance: {tl_params.L*1e9:.1f} nH/m")
    print(f"  Effective εᵣ: {tl_params.epsilon_eff:.2f}")
    
    # Create field visualization  
    print("\nGenerating field visualization...")
    solver = FieldSolver2D(geometry, params)
    solution = solver.solve_electrostatic({"signal": 1.0, "ground": 0.0})
    
    fig = create_complete_field_plot(solution)
    fig.suptitle(f"Stripline (Z₀ = {tl_params.Z0:.1f} Ω)", fontsize=14)
    plt.savefig("stripline_demo.png", dpi=150, bbox_inches='tight')
    print("Field plot saved as: stripline_demo.png")
    
    return tl_params, solution


def main():
    """Run demonstrations."""
    print("2D ELECTROMAGNETIC FIELD SOLVER DEMONSTRATION")
    print("=" * 60)
    
    # Microstrip demonstration
    try:
        microstrip_params, microstrip_solution = demonstrate_microstrip()
        print("\n✓ Microstrip analysis completed successfully")
    except Exception as e:
        print(f"\n✗ Microstrip analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Stripline demonstration
    try:
        stripline_params, stripline_solution = demonstrate_stripline()
        print("\n✓ Stripline analysis completed successfully")
    except Exception as e:
        print(f"\n✗ Stripline analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETED")
    print("="*60)
    print("\nThe 2D EM solver has demonstrated:")
    print("  • Microstrip transmission line analysis")
    print("  • Stripline transmission line analysis")
    print("  • RLGC parameter calculation")
    print("  • Comparison with analytical formulas")
    print("  • Electric field visualization")
    print("\nField distribution plots have been saved as PNG files.")


if __name__ == "__main__":
    main()