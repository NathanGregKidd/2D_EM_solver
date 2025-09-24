"""Example usage of the 2D EM solver."""

import numpy as np
import matplotlib.pyplot as plt

from em_solver.geometry import create_microstrip_geometry, create_stripline_geometry
from em_solver.solver import FieldSolver2D, SolverParameters
from em_solver.transmission_line import (
    calculate_transmission_line_parameters,
    calculate_characteristic_impedance_analytical
)
from em_solver.visualization import create_complete_field_plot


def example_microstrip_analysis():
    """Example: Analyze a typical PCB microstrip line."""
    print("="*60)
    print("MICROSTRIP TRANSMISSION LINE ANALYSIS")
    print("="*60)
    
    # Create geometry: 50Ω microstrip on FR4
    geometry = create_microstrip_geometry(
        substrate_width=0.005,    # 5mm wide substrate
        substrate_height=0.0016,  # 1.6mm FR4 substrate
        trace_width=0.003,       # 3mm trace width (approximately 50Ω)
        trace_thickness=0.000035, # 35μm copper thickness
        substrate_er=4.6,         # FR4 dielectric constant
        conductor_name="signal"
    )
    
    # Setup solver with reasonable resolution
    params = SolverParameters(
        nx=100,           # Grid resolution
        ny=100,
        frequency=1e9     # 1 GHz
    )
    
    # Calculate transmission line parameters
    print("Solving electromagnetic field problem...")
    tl_params = calculate_transmission_line_parameters(
        geometry=geometry,
        parameters=params,
        frequency=params.frequency,
        conductor_names=("signal", "ground")
    )
    
    # Calculate analytical result for comparison
    z0_analytical = calculate_characteristic_impedance_analytical(
        "microstrip",
        trace_width=0.003,
        substrate_height=0.0016,
        epsilon_r=4.6
    )
    
    # Print results
    print(f"\nGeometry Parameters:")
    print(f"  Substrate: 5.0 × 1.6 mm (εᵣ = 4.6)")
    print(f"  Trace: 3.0 × 0.035 mm")
    print(f"  Frequency: 1.0 GHz")
    
    print(f"\nNumerical Results:")
    print(f"  Characteristic Impedance: {tl_params.Z0:.1f} Ω")
    print(f"  Effective Permittivity: {tl_params.epsilon_eff:.2f}")
    print(f"  Capacitance: {tl_params.C*1e12:.1f} pF/m")
    print(f"  Inductance: {tl_params.L*1e9:.1f} nH/m")
    print(f"  Phase Velocity: {tl_params.v_phase/1e8:.2f} × 10⁸ m/s")
    
    print(f"\nAnalytical Comparison:")
    print(f"  Analytical Z₀: {z0_analytical:.1f} Ω")
    print(f"  Difference: {abs(tl_params.Z0 - z0_analytical):.1f} Ω")
    print(f"  Relative Error: {abs(tl_params.Z0 - z0_analytical)/z0_analytical*100:.1f}%")
    
    # Create field visualization
    print(f"\nGenerating field solution for visualization...")
    solver = FieldSolver2D(geometry, params)
    solution = solver.solve_electrostatic({"signal": 1.0, "ground": 0.0})
    
    fig = create_complete_field_plot(solution)
    fig.suptitle("Microstrip Transmission Line - 50Ω Target", fontsize=16)
    
    return solution, tl_params


def example_stripline_analysis():
    """Example: Analyze a stripline transmission line."""
    print("\n" + "="*60)
    print("STRIPLINE TRANSMISSION LINE ANALYSIS")
    print("="*60)
    
    # Create geometry: Symmetric stripline
    geometry = create_stripline_geometry(
        substrate_width=0.004,    # 4mm wide substrate
        substrate_height=0.002,   # 2mm between ground planes
        trace_width=0.0008,      # 0.8mm trace width
        trace_thickness=0.000035, # 35μm copper thickness
        substrate_er=4.2,         # Low-loss dielectric
        conductor_name="signal"
    )
    
    # Setup solver
    params = SolverParameters(nx=80, ny=80, frequency=2e9)  # 2 GHz
    
    # Calculate transmission line parameters
    print("Solving electromagnetic field problem...")
    tl_params = calculate_transmission_line_parameters(
        geometry=geometry,
        parameters=params,
        frequency=params.frequency,
        conductor_names=("signal", "ground")
    )
    
    # Calculate analytical result
    z0_analytical = calculate_characteristic_impedance_analytical(
        "stripline",
        trace_width=0.0008,
        substrate_height=0.002,
        epsilon_r=4.2
    )
    
    # Print results
    print(f"\nGeometry Parameters:")
    print(f"  Substrate: 4.0 × 2.0 mm (εᵣ = 4.2)")
    print(f"  Trace: 0.8 × 0.035 mm (centered)")
    print(f"  Frequency: 2.0 GHz")
    
    print(f"\nNumerical Results:")
    print(f"  Characteristic Impedance: {tl_params.Z0:.1f} Ω")
    print(f"  Effective Permittivity: {tl_params.epsilon_eff:.2f}")
    print(f"  Capacitance: {tl_params.C*1e12:.1f} pF/m")
    print(f"  Inductance: {tl_params.L*1e9:.1f} nH/m")
    print(f"  Phase Velocity: {tl_params.v_phase/1e8:.2f} × 10⁸ m/s")
    
    print(f"\nAnalytical Comparison:")
    print(f"  Analytical Z₀: {z0_analytical:.1f} Ω")
    print(f"  Difference: {abs(tl_params.Z0 - z0_analytical):.1f} Ω")
    print(f"  Relative Error: {abs(tl_params.Z0 - z0_analytical)/z0_analytical*100:.1f}%")
    
    # Create field visualization
    print(f"\nGenerating field solution for visualization...")
    solver = FieldSolver2D(geometry, params)
    solution = solver.solve_electrostatic({"signal": 1.0, "ground": 0.0})
    
    fig = create_complete_field_plot(solution)
    fig.suptitle("Stripline Transmission Line Analysis", fontsize=16)
    
    return solution, tl_params


def frequency_sweep_example():
    """Example: Frequency sweep analysis."""
    print("\n" + "="*60)
    print("FREQUENCY SWEEP ANALYSIS")
    print("="*60)
    
    # Create microstrip geometry
    geometry = create_microstrip_geometry(
        substrate_width=0.004,
        substrate_height=0.0016,
        trace_width=0.002,
        trace_thickness=0.000035,
        substrate_er=4.6
    )
    
    # Frequency sweep
    frequencies = np.logspace(8, 10, 10)  # 100 MHz to 10 GHz
    impedances = []
    phase_velocities = []
    
    params = SolverParameters(nx=60, ny=60)
    
    print("Performing frequency sweep...")
    for freq in frequencies:
        params.frequency = freq
        tl_params = calculate_transmission_line_parameters(
            geometry=geometry,
            parameters=params,
            frequency=freq,
            conductor_names=("copper", "ground")
        )
        impedances.append(tl_params.Z0)
        phase_velocities.append(tl_params.v_phase)
        print(f"  {freq/1e9:.2f} GHz: Z₀ = {tl_params.Z0:.1f} Ω, vₚ = {tl_params.v_phase/1e8:.2f}×10⁸ m/s")
    
    # Plot results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.semilogx(frequencies/1e9, impedances, 'bo-', linewidth=2, markersize=6)
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Characteristic Impedance (Ω)')
    ax1.set_title('Frequency Response - Characteristic Impedance')
    ax1.grid(True, alpha=0.3)
    
    ax2.semilogx(frequencies/1e9, np.array(phase_velocities)/1e8, 'ro-', linewidth=2, markersize=6)
    ax2.set_xlabel('Frequency (GHz)')
    ax2.set_ylabel('Phase Velocity (×10⁸ m/s)')
    ax2.set_title('Frequency Response - Phase Velocity')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def main():
    """Run all examples."""
    # Microstrip example
    microstrip_solution, microstrip_params = example_microstrip_analysis()
    
    # Stripline example
    stripline_solution, stripline_params = example_stripline_analysis()
    
    # Frequency sweep
    frequency_sweep_example()
    
    # Show plots
    plt.show()
    
    print("\n" + "="*60)
    print("EXAMPLES COMPLETED")
    print("="*60)
    print("\nThe 2D EM solver has successfully analyzed:")
    print("  1. Microstrip transmission line")
    print("  2. Stripline transmission line") 
    print("  3. Frequency response characteristics")
    print("\nField plots show the electric potential and field distributions.")
    print("Results are compared with analytical formulas for validation.")


if __name__ == '__main__':
    main()