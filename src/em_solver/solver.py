"""2D Electromagnetic field solver using finite difference method."""

import numpy as np
from scipy.sparse import diags, csr_matrix
from scipy.sparse.linalg import spsolve
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass

from .geometry import Geometry2D, Material


@dataclass 
class SolverParameters:
    """Parameters for the 2D field solver."""
    nx: int = 100  # Number of grid points in x direction
    ny: int = 100  # Number of grid points in y direction
    frequency: float = 1e9  # Frequency in Hz
    tolerance: float = 1e-6  # Convergence tolerance
    max_iterations: int = 1000  # Maximum iterations for iterative methods


@dataclass
class FieldSolution:
    """Results from 2D field solver."""
    electric_potential: np.ndarray  # Electric potential V(x,y)
    electric_field_x: np.ndarray   # Ex field component
    electric_field_y: np.ndarray   # Ey field component
    x_grid: np.ndarray             # X coordinates of grid points
    y_grid: np.ndarray             # Y coordinates of grid points
    geometry: Geometry2D           # Original geometry
    parameters: SolverParameters   # Solver parameters used
    
    @property
    def electric_field_magnitude(self) -> np.ndarray:
        """Calculate magnitude of electric field."""
        return np.sqrt(self.electric_field_x**2 + self.electric_field_y**2)


class FieldSolver2D:
    """2D electromagnetic field solver using finite difference method."""
    
    def __init__(self, geometry: Geometry2D, parameters: SolverParameters):
        """Initialize solver with geometry and parameters.
        
        Args:
            geometry: 2D geometry definition
            parameters: Solver parameters
        """
        self.geometry = geometry
        self.params = parameters
        
        # Create computational grid
        self.dx = geometry.width / (parameters.nx - 1)
        self.dy = geometry.height / (parameters.ny - 1)
        self.x_grid = np.linspace(0, geometry.width, parameters.nx)
        self.y_grid = np.linspace(0, geometry.height, parameters.ny)
        
        # Create material property arrays
        self._setup_material_arrays()
        
    def _setup_material_arrays(self) -> None:
        """Setup material property arrays on the computational grid."""
        self.epsilon_r = np.zeros((self.params.ny, self.params.nx))
        self.sigma = np.zeros((self.params.ny, self.params.nx))
        self.is_conductor = np.zeros((self.params.ny, self.params.nx), dtype=bool)
        
        for j in range(self.params.ny):
            for i in range(self.params.nx):
                x = self.x_grid[i]
                y = self.y_grid[j]
                material = self.geometry.get_material_at(x, y)
                
                self.epsilon_r[j, i] = material.epsilon_r
                self.sigma[j, i] = material.sigma
                self.is_conductor[j, i] = material.is_conductor
    
    def solve_electrostatic(self, conductor_voltages: Dict[str, float]) -> FieldSolution:
        """Solve 2D electrostatic problem using finite difference method.
        
        Args:
            conductor_voltages: Dictionary mapping conductor material names to voltages
            
        Returns:
            FieldSolution: Solution containing potential and field distributions
        """
        # Create coefficient matrix for Laplace equation with dielectric materials
        A, b = self._build_electrostatic_system(conductor_voltages)
        
        # Solve the linear system
        potential_flat = spsolve(A, b)
        potential = potential_flat.reshape((self.params.ny, self.params.nx))
        
        # Calculate electric field from potential (E = -grad(V))
        ex, ey = self._calculate_electric_field(potential)
        
        return FieldSolution(
            electric_potential=potential,
            electric_field_x=ex,
            electric_field_y=ey,
            x_grid=self.x_grid,
            y_grid=self.y_grid,
            geometry=self.geometry,
            parameters=self.params
        )
    
    def _build_electrostatic_system(self, conductor_voltages: Dict[str, float]) -> Tuple[csr_matrix, np.ndarray]:
        """Build linear system for electrostatic problem.
        
        The 2D Laplace equation with dielectrics:
        div(epsilon * grad(V)) = 0
        
        Using finite differences on a rectangular grid.
        """
        n_points = self.params.nx * self.params.ny
        
        # Initialize coefficient matrix and RHS vector
        row_indices = []
        col_indices = []
        data = []
        b = np.zeros(n_points)
        
        for j in range(self.params.ny):
            for i in range(self.params.nx):
                idx = j * self.params.nx + i
                
                # Check if this point is a conductor
                material = self.geometry.get_material_at(self.x_grid[i], self.y_grid[j])
                
                if material.is_conductor:
                    # Conductor boundary condition: V = specified voltage
                    row_indices.append(idx)
                    col_indices.append(idx)
                    data.append(1.0)
                    
                    # Set voltage if specified for this conductor
                    voltage = conductor_voltages.get(material.name, 0.0)
                    b[idx] = voltage
                    
                elif i == 0 or i == self.params.nx-1 or j == 0 or j == self.params.ny-1:
                    # Boundary conditions (assuming V = 0 at boundaries for now)
                    row_indices.append(idx)
                    col_indices.append(idx)
                    data.append(1.0)
                    b[idx] = 0.0
                    
                else:
                    # Interior point: finite difference approximation
                    # div(epsilon * grad(V)) ≈ 
                    # (epsilon_{i+1/2,j}*(V_{i+1,j}-V_{i,j}) - epsilon_{i-1/2,j}*(V_{i,j}-V_{i-1,j}))/dx^2 +
                    # (epsilon_{i,j+1/2}*(V_{i,j+1}-V_{i,j}) - epsilon_{i,j-1/2}*(V_{i,j}-V_{i,j-1}))/dy^2 = 0
                    
                    # Material properties at half-grid points (harmonic average)
                    eps_east = 2 * self.epsilon_r[j, i] * self.epsilon_r[j, i+1] / (self.epsilon_r[j, i] + self.epsilon_r[j, i+1])
                    eps_west = 2 * self.epsilon_r[j, i] * self.epsilon_r[j, i-1] / (self.epsilon_r[j, i] + self.epsilon_r[j, i-1])
                    eps_north = 2 * self.epsilon_r[j, i] * self.epsilon_r[j+1, i] / (self.epsilon_r[j, i] + self.epsilon_r[j+1, i])
                    eps_south = 2 * self.epsilon_r[j, i] * self.epsilon_r[j-1, i] / (self.epsilon_r[j, i] + self.epsilon_r[j-1, i])
                    
                    # Coefficients for 5-point stencil
                    coeff_center = -(eps_east + eps_west) / self.dx**2 - (eps_north + eps_south) / self.dy**2
                    coeff_east = eps_east / self.dx**2
                    coeff_west = eps_west / self.dx**2
                    coeff_north = eps_north / self.dy**2
                    coeff_south = eps_south / self.dy**2
                    
                    # Add entries to sparse matrix
                    row_indices.extend([idx] * 5)
                    col_indices.extend([idx, idx+1, idx-1, idx+self.params.nx, idx-self.params.nx])
                    data.extend([coeff_center, coeff_east, coeff_west, coeff_north, coeff_south])
        
        A = csr_matrix((data, (row_indices, col_indices)), shape=(n_points, n_points))
        return A, b
    
    def _calculate_electric_field(self, potential: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate electric field from potential using finite differences.
        
        E = -grad(V)
        """
        ex = np.zeros_like(potential)
        ey = np.zeros_like(potential)
        
        # Central differences in interior
        ex[1:-1, 1:-1] = -(potential[1:-1, 2:] - potential[1:-1, :-2]) / (2 * self.dx)
        ey[1:-1, 1:-1] = -(potential[2:, 1:-1] - potential[:-2, 1:-1]) / (2 * self.dy)
        
        # Forward/backward differences at boundaries
        ex[:, 0] = -(potential[:, 1] - potential[:, 0]) / self.dx
        ex[:, -1] = -(potential[:, -1] - potential[:, -2]) / self.dx
        ey[0, :] = -(potential[1, :] - potential[0, :]) / self.dy
        ey[-1, :] = -(potential[-1, :] - potential[-2, :]) / self.dy
        
        return ex, ey


def calculate_capacitance_matrix(geometry: Geometry2D, parameters: SolverParameters) -> np.ndarray:
    """Calculate capacitance matrix for multi-conductor system.
    
    Args:
        geometry: 2D geometry definition
        parameters: Solver parameters
        
    Returns:
        np.ndarray: Capacitance matrix [C] where Q = [C] * V
    """
    solver = FieldSolver2D(geometry, parameters)
    conductors = geometry.get_conductor_regions()
    
    if len(conductors) == 0:
        raise ValueError("No conductors found in geometry")
    
    # For transmission line analysis, we need at least signal conductor
    # Ground plane is often implicit (boundary condition)
    # We'll treat this as a two-conductor system: signal + ground (reference)
    
    # Get unique conductor materials (signal conductors)
    conductor_materials = list(set(rect.material.name for rect in conductors))
    
    # For single signal conductor case, create 2x2 matrix for signal + ground reference
    if len(conductor_materials) == 1:
        # Single conductor above ground plane case
        conductor_name = conductor_materials[0]
        
        # Calculate capacitance by solving with signal at 1V, ground at 0V
        conductor_voltages = {conductor_name: 1.0}
        solution = solver.solve_electrostatic(conductor_voltages)
        
        # Calculate total charge on signal conductor
        signal_charge = _calculate_conductor_charge(solution, conductor_name)
        
        # For single conductor case, C = Q/V
        capacitance = abs(signal_charge)  # C per unit length
        
        # Return 2x2 matrix for compatibility
        C_matrix = np.array([[capacitance, -capacitance], 
                            [-capacitance, capacitance]])
        
    else:
        # Multi-conductor case
        n_conductors = len(conductor_materials)
        C_matrix = np.zeros((n_conductors, n_conductors))
        
        # Calculate capacitance matrix by setting each conductor to 1V, others to 0V
        for i, conductor_name in enumerate(conductor_materials):
            # Set up voltage excitation
            conductor_voltages = {name: 0.0 for name in conductor_materials}
            conductor_voltages[conductor_name] = 1.0
            
            # Solve field problem
            solution = solver.solve_electrostatic(conductor_voltages)
            
            # Calculate charges on each conductor by integrating D·n over conductor surfaces
            for j, other_conductor in enumerate(conductor_materials):
                charge = _calculate_conductor_charge(solution, other_conductor)
                C_matrix[j, i] = charge  # C_ji = Q_j when V_i = 1V, V_k = 0 (k≠i)
    
    return C_matrix


def _calculate_conductor_charge(solution: FieldSolution, conductor_name: str) -> float:
    """Calculate total charge on a conductor surface.
    
    Uses Gauss's law: Q = ∫ epsilon * E · n dS
    """
    # Simple approximation: integrate normal electric field around conductor boundary
    charge = 0.0
    eps0 = 8.854e-12  # Permittivity of free space
    
    dx = solution.x_grid[1] - solution.x_grid[0]
    dy = solution.y_grid[1] - solution.y_grid[0]
    
    # Find conductor boundary points and estimate surface integral
    for j in range(1, solution.parameters.ny-1):
        for i in range(1, solution.parameters.nx-1):
            x = solution.x_grid[i]
            y = solution.y_grid[j]
            material = solution.geometry.get_material_at(x, y)
            
            if material.name == conductor_name:
                # Check if this is a boundary cell (conductor adjacent to dielectric)
                neighbors = [(i+1, j, dx, 0), (i-1, j, -dx, 0), 
                           (i, j+1, 0, dy), (i, j-1, 0, -dy)]
                
                for ni, nj, nx, ny in neighbors:
                    if (0 <= ni < solution.parameters.nx and 
                        0 <= nj < solution.parameters.ny):
                        
                        nx_mat = solution.geometry.get_material_at(
                            solution.x_grid[ni], solution.y_grid[nj]
                        )
                        
                        if not nx_mat.is_conductor:
                            # This is a conductor-dielectric boundary
                            # Calculate normal component of electric field
                            ex_avg = (solution.electric_field_x[j, i] + 
                                     solution.electric_field_x[nj, ni]) / 2
                            ey_avg = (solution.electric_field_y[j, i] + 
                                     solution.electric_field_y[nj, ni]) / 2
                            
                            # Normal field component (pointing outward from conductor)
                            if abs(nx) > 0:  # Horizontal boundary
                                e_normal = ex_avg * (nx / abs(nx))
                                ds = abs(dy)
                            else:  # Vertical boundary
                                e_normal = ey_avg * (ny / abs(ny))
                                ds = abs(dx)
                            
                            # Surface charge density: D = epsilon * E
                            epsilon = eps0 * nx_mat.epsilon_r
                            surface_charge = epsilon * e_normal * ds
                            charge += surface_charge
    
    return charge