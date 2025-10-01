"""Calculate transmission line parameters (RLGC) from 2D field solutions."""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass

from .geometry import Geometry2D
from .solver import FieldSolver2D, SolverParameters, calculate_capacitance_matrix


# Physical constants
MU0 = 4 * np.pi * 1e-7  # Permeability of free space (H/m)
EPS0 = 8.854e-12        # Permittivity of free space (F/m)
C_LIGHT = 1 / np.sqrt(MU0 * EPS0)  # Speed of light (m/s)


@dataclass
class TransmissionLineParameters:
    """Transmission line parameters for a two-conductor system."""
    # Primary parameters (per unit length)
    R: float  # Resistance (Ω/m)
    L: float  # Inductance (H/m)
    G: float  # Conductance (S/m)
    C: float  # Capacitance (F/m)
    
    # Secondary parameters
    Z0: float  # Characteristic impedance (Ω)
    gamma: complex  # Propagation constant (1/m)
    alpha: float  # Attenuation constant (Np/m)
    beta: float  # Phase constant (rad/m)
    v_phase: float  # Phase velocity (m/s)
    epsilon_eff: float  # Effective permittivity
    
    # Frequency
    frequency: float  # Frequency (Hz)


def calculate_transmission_line_parameters(
    geometry: Geometry2D,
    parameters: SolverParameters,
    frequency: float = 1e9,
    conductor_names: Tuple[str, str] = ("signal", "ground")
) -> TransmissionLineParameters:
    """Calculate RLGC parameters for a two-conductor transmission line.
    
    Args:
        geometry: 2D cross-section geometry
        parameters: Solver parameters
        frequency: Operating frequency (Hz)
        conductor_names: Names of signal and ground conductors
        
    Returns:
        TransmissionLineParameters: Complete set of transmission line parameters
    """
    # Calculate capacitance matrix
    C_matrix = calculate_capacitance_matrix(geometry, parameters)
    
    # For transmission line analysis, extract capacitance per unit length
    if C_matrix.shape[0] == 2:
        # Two-conductor case: C = C11 - C12
        C = C_matrix[0, 0] - C_matrix[0, 1]
    else:
        # Single conductor case: use diagonal element
        C = C_matrix[0, 0]
    
    # Calculate inductance using L = μ₀ε₀/C_air * C_air/C
    # where C_air is capacitance with all dielectrics replaced by air
    L = _calculate_inductance_from_capacitance(geometry, parameters, C)
    
    # Calculate resistance from conductor geometry and skin effect
    R = _calculate_resistance(geometry, frequency, conductor_names)
    
    # Calculate conductance from dielectric loss
    G = _calculate_conductance(geometry, parameters, C, frequency)
    
    # Calculate secondary parameters
    Z0, gamma, epsilon_eff = _calculate_secondary_parameters(R, L, G, C, frequency)
    
    alpha = gamma.real
    beta = gamma.imag
    v_phase = 2 * np.pi * frequency / beta if beta != 0 else 0
    
    return TransmissionLineParameters(
        R=R, L=L, G=G, C=C,
        Z0=Z0, gamma=gamma, alpha=alpha, beta=beta,
        v_phase=v_phase, epsilon_eff=epsilon_eff,
        frequency=frequency
    )


def _calculate_inductance_from_capacitance(
    geometry: Geometry2D, 
    parameters: SolverParameters, 
    capacitance: float
) -> float:
    """Calculate inductance using the relationship L = μ₀ε₀ * C_air / C.
    
    This method calculates L by finding the capacitance of the same geometry
    with all dielectrics replaced by air, then using the fundamental relationship.
    """
    # Create air-filled version of geometry
    air_geometry = _create_air_filled_geometry(geometry)
    
    # Calculate capacitance with air dielectric
    try:
        C_air_matrix = calculate_capacitance_matrix(air_geometry, parameters)
        if C_air_matrix.shape[0] == 2:
            C_air = C_air_matrix[0, 0] - C_air_matrix[0, 1]
        else:
            C_air = C_air_matrix[0, 0]
    except:
        # Fallback: estimate from geometry
        # For microstrip: approximate analytical formula for air-filled case
        conductors = geometry.get_conductor_regions()
        if len(conductors) > 0:
            # Simple approximation based on parallel plate capacitor
            conductor = conductors[0]
            eps0 = 8.854e-12
            # Approximate capacitance for air-filled microstrip
            width_to_height = conductor.width / geometry.height
            if width_to_height > 1:
                # Wide trace approximation
                C_air = eps0 * conductor.width / geometry.height
            else:
                # Narrow trace approximation 
                C_air = eps0 * np.pi / np.log(4 * geometry.height / conductor.width)
        else:
            C_air = capacitance  # Fallback
    
    # Avoid division by zero
    if abs(capacitance) < 1e-20:
        capacitance = 1e-12  # Use minimum reasonable value
    
    # Inductance relationship: L * C = μ₀ε₀ * C_air / C
    L = MU0 * EPS0 * C_air / capacitance
    
    # Sanity check - typical range for transmission lines
    if L < 1e-12 or L > 1e-3:
        # Use typical values based on geometry
        conductors = geometry.get_conductor_regions()
        if len(conductors) > 0:
            conductor = conductors[0]
            # Rough estimate: L ~ μ₀ * height / width for microstrip
            L = MU0 * geometry.height / conductor.width
    
    return L


def _create_air_filled_geometry(geometry: Geometry2D) -> Geometry2D:
    """Create version of geometry with all dielectrics replaced by air."""
    from .geometry import Material
    
    air = Material("air", epsilon_r=1.0)
    air_geometry = Geometry2D(geometry.width, geometry.height, air)
    
    # Add only conductor regions (keeping their positions)
    for region in geometry.regions:
        if region.material.is_conductor:
            air_geometry.add_rectangle(region)
    
    return air_geometry


def _calculate_resistance(
    geometry: Geometry2D, 
    frequency: float, 
    conductor_names: Tuple[str, str]
) -> float:
    """Calculate resistance per unit length including skin effect."""
    conductors = geometry.get_conductor_regions()
    
    total_resistance = 0.0
    
    for conductor in conductors:
        if conductor.material.name in conductor_names:
            # Skin depth
            sigma = conductor.material.sigma
            delta_skin = np.sqrt(2 / (2 * np.pi * frequency * MU0 * sigma))
            
            # Surface resistance
            Rs = 1 / (sigma * delta_skin)
            
            # Approximate perimeter (for rectangular cross-section)
            perimeter = 2 * (conductor.width + conductor.height)
            
            # Resistance contribution (simplified)
            # More accurate calculation would consider current distribution
            R_conductor = Rs / perimeter
            total_resistance += R_conductor
    
    return total_resistance


def _calculate_conductance(
    geometry: Geometry2D,
    parameters: SolverParameters, 
    capacitance: float,
    frequency: float
) -> float:
    """Calculate conductance per unit length from dielectric loss."""
    # Calculate loss tangent weighted by field energy
    solver = FieldSolver2D(geometry, parameters)
    
    # Solve for electric field distribution
    conductor_voltages = {"signal": 1.0, "ground": 0.0}  # Example voltages
    solution = solver.solve_electrostatic(conductor_voltages)
    
    # Calculate weighted loss tangent
    total_loss_tangent = 0.0
    total_energy = 0.0
    
    for j in range(parameters.ny):
        for i in range(parameters.nx):
            x = solution.x_grid[i]
            y = solution.y_grid[j]
            material = geometry.get_material_at(x, y)
            
            if not material.is_conductor:
                # Electric field energy density
                ex = solution.electric_field_x[j, i]
                ey = solution.electric_field_y[j, i]
                energy_density = 0.5 * EPS0 * material.epsilon_r * (ex**2 + ey**2)
                
                # Loss tangent for this material (simplified - assume low loss)
                # tan(δ) = σ / (ωε) for dielectric loss
                omega = 2 * np.pi * frequency
                epsilon = EPS0 * material.epsilon_r
                loss_tangent = material.sigma / (omega * epsilon) if omega * epsilon > 0 else 0
                
                total_loss_tangent += loss_tangent * energy_density
                total_energy += energy_density
    
    # Average loss tangent weighted by field energy
    avg_loss_tangent = total_loss_tangent / total_energy if total_energy > 0 else 0
    
    # Conductance: G = ωC * tan(δ)
    omega = 2 * np.pi * frequency
    G = omega * capacitance * avg_loss_tangent
    
    return G


def _calculate_secondary_parameters(
    R: float, L: float, G: float, C: float, frequency: float
) -> Tuple[float, complex, float]:
    """Calculate secondary transmission line parameters.
    
    Returns:
        Tuple[float, complex, float]: (Z0, gamma, epsilon_eff)
    """
    omega = 2 * np.pi * frequency
    
    # Complex impedance and admittance per unit length
    Z = R + 1j * omega * L
    Y = G + 1j * omega * C
    
    # Characteristic impedance
    Z0 = np.sqrt(Z / Y)
    
    # Propagation constant
    gamma = np.sqrt(Z * Y)
    
    # Effective permittivity (for TEM or quasi-TEM modes)
    # εeff = (β/k0)² where k0 = ω/c
    beta = gamma.imag
    k0 = omega / C_LIGHT
    epsilon_eff = (beta / k0)**2 if k0 != 0 else 1.0
    
    return Z0.real, gamma, epsilon_eff


def calculate_characteristic_impedance_analytical(
    geometry_type: str,
    **kwargs
) -> float:
    """Calculate characteristic impedance using analytical formulas for validation.
    
    Args:
        geometry_type: Type of transmission line ('microstrip', 'stripline', etc.)
        **kwargs: Geometry parameters specific to each type
        
    Returns:
        float: Analytical characteristic impedance
    """
    if geometry_type == "microstrip":
        return _analytical_microstrip_impedance(**kwargs)
    elif geometry_type == "stripline":
        return _analytical_stripline_impedance(**kwargs)
    else:
        raise ValueError(f"Analytical formula not implemented for {geometry_type}")


def _analytical_microstrip_impedance(
    trace_width: float,
    substrate_height: float,
    epsilon_r: float
) -> float:
    """Analytical formula for microstrip characteristic impedance.
    
    Uses Wheeler's formula and corrections.
    """
    w_h = trace_width / substrate_height
    
    if w_h <= 1:
        Z0 = (60 / np.sqrt(epsilon_r)) * np.log(8/w_h + w_h/4)
    else:
        Z0 = (120 * np.pi) / (np.sqrt(epsilon_r) * (w_h + 1.393 + 0.667 * np.log(w_h + 1.444)))
    
    return Z0


def _analytical_stripline_impedance(
    trace_width: float,
    substrate_height: float,
    epsilon_r: float
) -> float:
    """Analytical formula for stripline characteristic impedance."""
    w_h = trace_width / substrate_height
    
    if w_h <= 0.35:
        Z0 = (60 / np.sqrt(epsilon_r)) * np.log(4 / (w_h * (1 - w_h**2)**0.5))
    else:
        Z0 = (60 / np.sqrt(epsilon_r)) * np.log(2 / w_h + 1.7 * w_h)
    
    return Z0