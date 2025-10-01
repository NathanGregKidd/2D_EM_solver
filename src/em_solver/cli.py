"""Command-line interface for the 2D EM solver."""

import argparse
import sys
import json
from typing import Dict, Any

from .geometry import create_microstrip_geometry, create_stripline_geometry
from .solver import FieldSolver2D, SolverParameters
from .transmission_line import (
    calculate_transmission_line_parameters,
    calculate_characteristic_impedance_analytical
)
from .visualization import create_complete_field_plot, save_field_plots


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="2D Electromagnetic Field Solver for Transmission Lines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze microstrip transmission line
  2d-em-solver microstrip --width 0.001 --height 0.0016 --trace-width 0.001 --trace-thickness 0.000035
  
  # Analyze stripline with custom parameters
  2d-em-solver stripline --width 0.002 --height 0.001 --trace-width 0.0005 --trace-thickness 0.000018 --er 4.2
  
  # Save plots to files
  2d-em-solver microstrip --width 0.001 --height 0.0016 --trace-width 0.001 --trace-thickness 0.000035 --save-plots
        """
    )
    
    # Subcommands for different transmission line types
    subparsers = parser.add_subparsers(dest='geometry_type', help='Transmission line geometry')
    
    # Microstrip subcommand
    microstrip_parser = subparsers.add_parser('microstrip', help='Microstrip transmission line')
    add_microstrip_arguments(microstrip_parser)
    
    # Stripline subcommand
    stripline_parser = subparsers.add_parser('stripline', help='Stripline transmission line')
    add_stripline_arguments(stripline_parser)
    
    # Global options
    parser.add_argument('--frequency', type=float, default=1e9,
                       help='Operating frequency in Hz (default: 1e9)')
    parser.add_argument('--nx', type=int, default=100,
                       help='Number of grid points in x direction (default: 100)')
    parser.add_argument('--ny', type=int, default=100,
                       help='Number of grid points in y direction (default: 100)')
    parser.add_argument('--save-plots', action='store_true',
                       help='Save field plots to files')
    parser.add_argument('--show-plots', action='store_true',
                       help='Display plots on screen')
    parser.add_argument('--output-json', type=str,
                       help='Save results to JSON file')
    parser.add_argument('--compare-analytical', action='store_true',
                       help='Compare with analytical formulas')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    return parser.parse_args()


def add_microstrip_arguments(parser):
    """Add microstrip-specific arguments."""
    parser.add_argument('--width', type=float, required=True,
                       help='Substrate width in meters')
    parser.add_argument('--height', type=float, required=True,
                       help='Substrate height in meters')
    parser.add_argument('--trace-width', type=float, required=True,
                       help='Trace width in meters')
    parser.add_argument('--trace-thickness', type=float, required=True,
                       help='Trace thickness in meters')
    parser.add_argument('--er', type=float, default=4.6,
                       help='Substrate relative permittivity (default: 4.6)')
    parser.add_argument('--conductor', type=str, default='copper',
                       help='Conductor material name (default: copper)')


def add_stripline_arguments(parser):
    """Add stripline-specific arguments."""
    parser.add_argument('--width', type=float, required=True,
                       help='Substrate width in meters')
    parser.add_argument('--height', type=float, required=True,
                       help='Substrate height in meters')
    parser.add_argument('--trace-width', type=float, required=True,
                       help='Trace width in meters')
    parser.add_argument('--trace-thickness', type=float, required=True,
                       help='Trace thickness in meters')
    parser.add_argument('--er', type=float, default=4.6,
                       help='Substrate relative permittivity (default: 4.6)')
    parser.add_argument('--conductor', type=str, default='copper',
                       help='Conductor material name (default: copper)')


def create_geometry_from_args(args):
    """Create geometry object from command line arguments."""
    if args.geometry_type == 'microstrip':
        return create_microstrip_geometry(
            substrate_width=args.width,
            substrate_height=args.height,
            trace_width=args.trace_width,
            trace_thickness=args.trace_thickness,
            substrate_er=args.er,
            conductor_name=args.conductor
        )
    elif args.geometry_type == 'stripline':
        return create_stripline_geometry(
            substrate_width=args.width,
            substrate_height=args.height,
            trace_width=args.trace_width,
            trace_thickness=args.trace_thickness,
            substrate_er=args.er,
            conductor_name=args.conductor
        )
    else:
        raise ValueError(f"Unknown geometry type: {args.geometry_type}")


def print_results(params, args):
    """Print transmission line parameters."""
    print("\n" + "="*60)
    print("2D ELECTROMAGNETIC FIELD SOLVER RESULTS")
    print("="*60)
    
    print(f"\nGeometry: {args.geometry_type.title()}")
    print(f"Frequency: {args.frequency/1e9:.3f} GHz")
    
    print(f"\nGeometry Parameters:")
    print(f"  Width: {args.width*1000:.3f} mm")
    print(f"  Height: {args.height*1000:.3f} mm")
    print(f"  Trace Width: {args.trace_width*1000:.3f} mm")
    print(f"  Trace Thickness: {args.trace_thickness*1000:.3f} μm")
    print(f"  Substrate εᵣ: {args.er:.2f}")
    
    print(f"\nTransmission Line Parameters:")
    print(f"  Resistance (R): {params.R*1000:.3f} mΩ/m")
    print(f"  Inductance (L): {params.L*1e9:.3f} nH/m")
    print(f"  Conductance (G): {params.G*1e6:.3f} μS/m")
    print(f"  Capacitance (C): {params.C*1e12:.3f} pF/m")
    
    print(f"\nCharacteristic Parameters:")
    print(f"  Characteristic Impedance (Z₀): {params.Z0:.2f} Ω")
    print(f"  Effective Permittivity (εₑff): {params.epsilon_eff:.3f}")
    print(f"  Phase Velocity: {params.v_phase/1e8:.3f} × 10⁸ m/s")
    print(f"  Attenuation Constant (α): {params.alpha*1000:.3f} mNp/m")
    print(f"  Phase Constant (β): {params.beta:.3f} rad/m")
    
    # Compare with analytical if requested
    if args.compare_analytical:
        try:
            analytical_z0 = calculate_characteristic_impedance_analytical(
                args.geometry_type,
                trace_width=args.trace_width,
                substrate_height=args.height,
                epsilon_r=args.er
            )
            print(f"\nAnalytical Comparison:")
            print(f"  Analytical Z₀: {analytical_z0:.2f} Ω")
            print(f"  Numerical Z₀: {params.Z0:.2f} Ω")
            print(f"  Difference: {abs(params.Z0 - analytical_z0):.2f} Ω ({abs(params.Z0 - analytical_z0)/analytical_z0*100:.1f}%)")
        except Exception as e:
            if args.verbose:
                print(f"\nAnalytical comparison failed: {e}")


def save_results_json(params, args, filename):
    """Save results to JSON file."""
    results = {
        'geometry_type': args.geometry_type,
        'frequency_hz': args.frequency,
        'geometry_parameters': {
            'width_m': args.width,
            'height_m': args.height,
            'trace_width_m': args.trace_width,
            'trace_thickness_m': args.trace_thickness,
            'substrate_er': args.er,
            'conductor': args.conductor
        },
        'transmission_line_parameters': {
            'R_ohm_per_m': params.R,
            'L_h_per_m': params.L,
            'G_s_per_m': params.G,
            'C_f_per_m': params.C,
            'Z0_ohm': params.Z0,
            'epsilon_eff': params.epsilon_eff,
            'v_phase_m_per_s': params.v_phase,
            'alpha_np_per_m': params.alpha,
            'beta_rad_per_m': params.beta
        },
        'solver_parameters': {
            'nx': args.nx,
            'ny': args.ny
        }
    }
    
    if args.compare_analytical:
        try:
            analytical_z0 = calculate_characteristic_impedance_analytical(
                args.geometry_type,
                trace_width=args.trace_width,
                substrate_height=args.height,
                epsilon_r=args.er
            )
            results['analytical_comparison'] = {
                'analytical_z0_ohm': analytical_z0,
                'difference_ohm': abs(params.Z0 - analytical_z0),
                'relative_error_percent': abs(params.Z0 - analytical_z0)/analytical_z0*100
            }
        except Exception as e:
            results['analytical_comparison'] = {'error': str(e)}
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {filename}")


def main():
    """Main entry point for CLI."""
    args = parse_arguments()
    
    if args.geometry_type is None:
        print("Error: Please specify geometry type (microstrip or stripline)")
        print("Use --help for more information")
        sys.exit(1)
    
    try:
        # Create geometry
        if args.verbose:
            print("Creating geometry...")
        
        geometry = create_geometry_from_args(args)
        
        # Setup solver parameters
        params = SolverParameters(
            nx=args.nx,
            ny=args.ny,
            frequency=args.frequency
        )
        
        # Calculate transmission line parameters
        if args.verbose:
            print("Solving electromagnetic field problem...")
        
        tl_params = calculate_transmission_line_parameters(
            geometry=geometry,
            parameters=params,
            frequency=args.frequency,
            conductor_names=(args.conductor, "ground")
        )
        
        # Print results
        print_results(tl_params, args)
        
        # Save JSON results if requested
        if args.output_json:
            save_results_json(tl_params, args, args.output_json)
        
        # Create and save/show plots if requested
        if args.save_plots or args.show_plots:
            if args.verbose:
                print("Generating field solution for visualization...")
            
            # Solve field for visualization
            solver = FieldSolver2D(geometry, params)
            conductor_voltages = {args.conductor: 1.0, "ground": 0.0}
            solution = solver.solve_electrostatic(conductor_voltages)
            
            if args.save_plots:
                if args.verbose:
                    print("Saving plots...")
                filenames = save_field_plots(solution, f"{args.geometry_type}_analysis")
                print(f"\nPlots saved: {', '.join(filenames)}")
            
            if args.show_plots:
                if args.verbose:
                    print("Displaying plots...")
                import matplotlib.pyplot as plt
                create_complete_field_plot(solution)
                plt.show()
    
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()