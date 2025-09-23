"""Simple test to debug the solver."""

import sys
import os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from em_solver.geometry import create_microstrip_geometry
from em_solver.solver import FieldSolver2D, SolverParameters, calculate_capacitance_matrix
from em_solver.transmission_line import calculate_transmission_line_parameters

# Create simple microstrip geometry with thicker trace for testing
print("Creating microstrip geometry...")
geometry = create_microstrip_geometry(
    substrate_width=0.003,    # 3mm wide
    substrate_height=0.0016,  # 1.6mm FR4
    trace_width=0.001,       # 1mm trace
    trace_thickness=0.0002,   # 200μm copper (much thicker for testing)
    substrate_er=4.6          # FR4
)

print(f"Geometry created with {len(geometry.regions)} regions")
print(f"Conductors found: {len(geometry.get_conductor_regions())}")

for i, region in enumerate(geometry.regions):
    print(f"  Region {i}: {region.material.name}, conductor={region.material.is_conductor}")

# Test solver setup
print("\nSetting up solver...")
params = SolverParameters(nx=50, ny=50, frequency=1e9)  # Higher resolution
solver = FieldSolver2D(geometry, params)

# Test conductor detection
print("\nDebugging conductor detection...")
print(f"Trace region: x=[{geometry.regions[1].x_min:.6f}, {geometry.regions[1].x_max:.6f}]")
print(f"Trace region: y=[{geometry.regions[1].y_min:.6f}, {geometry.regions[1].y_max:.6f}]")
print(f"Grid x range: [{solver.x_grid[0]:.6f}, {solver.x_grid[-1]:.6f}]")
print(f"Grid y range: [{solver.y_grid[0]:.6f}, {solver.y_grid[-1]:.6f}]")
print(f"Grid dx: {solver.dx:.6f}, dy: {solver.dy:.6f}")

# Check specific grid points
trace_region = geometry.regions[1]  # Copper trace
for j in range(params.ny):
    for i in range(params.nx):
        x = solver.x_grid[i]
        y = solver.y_grid[j]
        if trace_region.contains_point(x, y):
            print(f"Grid point ({i},{j}) at ({x:.6f},{y:.6f}) is in trace")
            break
    else:
        continue
    break
else:
    print("No grid points found in trace region!")
    
    # Check if trace is too thin
    mid_x = (trace_region.x_min + trace_region.x_max) / 2
    mid_y = (trace_region.y_min + trace_region.y_max) / 2
    print(f"Trace center: ({mid_x:.6f}, {mid_y:.6f})")
    
    # Find closest grid points
    i_closest = np.argmin(np.abs(solver.x_grid - mid_x))
    j_closest = np.argmin(np.abs(solver.y_grid - mid_y))
    print(f"Closest grid point: ({i_closest},{j_closest}) at ({solver.x_grid[i_closest]:.6f},{solver.y_grid[j_closest]:.6f})")
    
    # Check material at closest point
    material = geometry.get_material_at(solver.x_grid[i_closest], solver.y_grid[j_closest])
    print(f"Material at closest point: {material.name}, conductor={material.is_conductor}")

# Test electrostatic solve
print("\nSolving electrostatic problem...")
conductor_voltages = {"copper": 1.0}
solution = solver.solve_electrostatic(conductor_voltages)

print("Field solution completed")
print(f"Potential range: [{np.min(solution.electric_potential):.3f}, {np.max(solution.electric_potential):.3f}]")

# Test capacitance calculation
print("\nCalculating capacitance matrix...")
import numpy as np
try:
    C_matrix = calculate_capacitance_matrix(geometry, params)
    print(f"Capacitance matrix shape: {C_matrix.shape}")
    print(f"Capacitance matrix:\n{C_matrix}")
    
    if C_matrix.shape[0] >= 1:
        if C_matrix.shape[0] == 2:
            C = C_matrix[0, 0] - C_matrix[0, 1]
        else:
            C = C_matrix[0, 0]
        print(f"Extracted capacitance: {C:.3e} F/m")
        print(f"Capacitance: {C*1e12:.3f} pF/m")
    
except Exception as e:
    print(f"Capacitance calculation failed: {e}")
    import traceback
    traceback.print_exc()

print("\nDebug test completed.")