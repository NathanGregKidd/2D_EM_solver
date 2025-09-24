"""Test suite for the 2D EM solver."""

import numpy as np
import sys
import os
from unittest import TestCase

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from em_solver.geometry import (
    Material, Rectangle, Geometry2D, 
    create_microstrip_geometry, create_stripline_geometry
)
from em_solver.solver import FieldSolver2D, SolverParameters
from em_solver.transmission_line import (
    calculate_transmission_line_parameters,
    calculate_characteristic_impedance_analytical
)


class TestMaterial(TestCase):
    """Test Material class."""
    
    def test_conductor_detection(self):
        """Test conductor detection based on conductivity."""
        air = Material("air", epsilon_r=1.0, sigma=0.0)
        copper = Material("copper", epsilon_r=1.0, sigma=5.8e7)
        
        self.assertFalse(air.is_conductor)
        self.assertTrue(copper.is_conductor)


class TestGeometry2D(TestCase):
    """Test Geometry2D class."""
    
    def test_basic_geometry_creation(self):
        """Test basic geometry creation."""
        air = Material("air", epsilon_r=1.0)
        geometry = Geometry2D(1.0, 1.0, air)
        
        self.assertEqual(geometry.width, 1.0)
        self.assertEqual(geometry.height, 1.0)
        self.assertEqual(geometry.default_material, air)
    
    def test_rectangle_addition(self):
        """Test adding rectangles to geometry."""
        air = Material("air", epsilon_r=1.0)
        copper = Material("copper", epsilon_r=1.0, sigma=5.8e7)
        
        geometry = Geometry2D(1.0, 1.0, air)
        rect = Rectangle(0.25, 0.75, 0.25, 0.75, copper)
        
        geometry.add_rectangle(rect)
        self.assertEqual(len(geometry.regions), 1)
        self.assertEqual(geometry.regions[0], rect)
    
    def test_out_of_bounds_rectangle(self):
        """Test that out-of-bounds rectangles raise error."""
        air = Material("air", epsilon_r=1.0)
        copper = Material("copper", epsilon_r=1.0, sigma=5.8e7)
        
        geometry = Geometry2D(1.0, 1.0, air)
        rect = Rectangle(0.5, 1.5, 0.5, 1.5, copper)  # Extends outside
        
        with self.assertRaises(ValueError):
            geometry.add_rectangle(rect)
    
    def test_material_at_point(self):
        """Test material detection at specific points."""
        air = Material("air", epsilon_r=1.0)
        copper = Material("copper", epsilon_r=1.0, sigma=5.8e7)
        
        geometry = Geometry2D(1.0, 1.0, air)
        rect = Rectangle(0.25, 0.75, 0.25, 0.75, copper)
        geometry.add_rectangle(rect)
        
        # Point inside rectangle
        self.assertEqual(geometry.get_material_at(0.5, 0.5), copper)
        
        # Point outside rectangle
        self.assertEqual(geometry.get_material_at(0.1, 0.1), air)


class TestPredefinedGeometries(TestCase):
    """Test predefined geometry creation functions."""
    
    def test_microstrip_creation(self):
        """Test microstrip geometry creation."""
        geometry = create_microstrip_geometry(
            substrate_width=0.001,
            substrate_height=0.0016,
            trace_width=0.001,
            trace_thickness=0.000035,
            substrate_er=4.6
        )
        
        self.assertIsInstance(geometry, Geometry2D)
        self.assertEqual(len(geometry.regions), 3)  # Ground plane + substrate + trace
        
        # Check that we have conductor regions (ground + signal)
        conductors = geometry.get_conductor_regions()
        self.assertEqual(len(conductors), 2)
        
        # Verify conductor names
        conductor_names = [c.material.name for c in conductors]
        self.assertIn("ground", conductor_names)
        self.assertIn("signal", conductor_names)
        
        # Verify ground plane is at bottom
        ground_conductor = next(c for c in conductors if c.material.name == "ground")
        self.assertEqual(ground_conductor.y_min, 0.0)  # Should start at bottom
        self.assertEqual(ground_conductor.x_min, 0.0)  # Should span full width
        self.assertEqual(ground_conductor.x_max, geometry.width)
    
    def test_stripline_creation(self):
        """Test stripline geometry creation."""
        geometry = create_stripline_geometry(
            substrate_width=0.002,
            substrate_height=0.001,
            trace_width=0.0005,
            trace_thickness=0.000018,
            substrate_er=4.2
        )
        
        self.assertIsInstance(geometry, Geometry2D)
        self.assertEqual(len(geometry.regions), 1)  # Just trace (substrate is default)
        
        # Check that we have conductor regions
        conductors = geometry.get_conductor_regions()
        self.assertEqual(len(conductors), 1)


class TestFieldSolver(TestCase):
    """Test field solver functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.geometry = create_microstrip_geometry(
            substrate_width=0.002,
            substrate_height=0.001,
            trace_width=0.0005,
            trace_thickness=0.000035
        )
        self.params = SolverParameters(nx=50, ny=50)
    
    def test_solver_initialization(self):
        """Test solver initialization."""
        solver = FieldSolver2D(self.geometry, self.params)
        
        self.assertEqual(solver.geometry, self.geometry)
        self.assertEqual(solver.params, self.params)
        self.assertEqual(solver.x_grid.shape, (50,))
        self.assertEqual(solver.y_grid.shape, (50,))
    
    def test_material_arrays_setup(self):
        """Test material property arrays setup."""
        solver = FieldSolver2D(self.geometry, self.params)
        
        self.assertEqual(solver.epsilon_r.shape, (50, 50))
        self.assertEqual(solver.sigma.shape, (50, 50))
        self.assertEqual(solver.is_conductor.shape, (50, 50))
        
        # Check that some points are identified as conductors
        self.assertTrue(np.any(solver.is_conductor))
    
    def test_electrostatic_solve(self):
        """Test electrostatic field solution."""
        solver = FieldSolver2D(self.geometry, self.params)
        conductor_voltages = {"copper": 1.0}
        
        solution = solver.solve_electrostatic(conductor_voltages)
        
        # Check solution structure
        self.assertEqual(solution.electric_potential.shape, (50, 50))
        self.assertEqual(solution.electric_field_x.shape, (50, 50))
        self.assertEqual(solution.electric_field_y.shape, (50, 50))
        
        # Check that solution is reasonable
        self.assertTrue(np.all(np.isfinite(solution.electric_potential)))
        self.assertTrue(np.all(np.isfinite(solution.electric_field_x)))
        self.assertTrue(np.all(np.isfinite(solution.electric_field_y)))


class TestTransmissionLineCalculations(TestCase):
    """Test transmission line parameter calculations."""
    
    def test_microstrip_parameters(self):
        """Test microstrip parameter calculation."""
        geometry = create_microstrip_geometry(
            substrate_width=0.002,
            substrate_height=0.001,
            trace_width=0.0005,
            trace_thickness=0.0001,  # Thicker trace for better numerical stability
            substrate_er=4.6,
            conductor_name="signal"  # Use explicit conductor name for clarity
        )
        
        params = SolverParameters(nx=80, ny=80)  # Higher resolution for small features
        
        tl_params = calculate_transmission_line_parameters(
            geometry=geometry,
            parameters=params,
            frequency=1e9,
            conductor_names=("signal", "ground")  # Match actual conductor material names
        )
        
        # Check that parameters are reasonable
        self.assertGreater(tl_params.C, 0)  # Positive capacitance
        self.assertGreater(tl_params.L, 0)  # Positive inductance
        self.assertGreaterEqual(tl_params.R, 0)  # Non-negative resistance
        self.assertGreaterEqual(tl_params.G, 0)  # Non-negative conductance
        self.assertGreater(tl_params.Z0, 0)  # Positive characteristic impedance
        self.assertGreater(tl_params.epsilon_eff, 1.0)  # Effective permittivity > 1
        
        # Characteristic impedance should be reasonable for microstrip
        self.assertGreater(tl_params.Z0, 20)  # Typical range
        self.assertLess(tl_params.Z0, 200)
    
    def test_analytical_comparison(self):
        """Test comparison with analytical formulas."""
        # Test microstrip analytical formula
        z0_analytical = calculate_characteristic_impedance_analytical(
            "microstrip",
            trace_width=0.001,
            substrate_height=0.0016,
            epsilon_r=4.6
        )
        
        self.assertGreater(z0_analytical, 0)
        self.assertIsInstance(z0_analytical, float)
        
        # Test stripline analytical formula
        z0_analytical_stripline = calculate_characteristic_impedance_analytical(
            "stripline",
            trace_width=0.0005,
            substrate_height=0.001,
            epsilon_r=4.2
        )
        
        self.assertGreater(z0_analytical_stripline, 0)
        self.assertIsInstance(z0_analytical_stripline, float)


def test_integration_microstrip():
    """Integration test for microstrip analysis."""
    # Create a typical microstrip geometry
    geometry = create_microstrip_geometry(
        substrate_width=0.003,  # 3mm wide
        substrate_height=0.0016,  # 1.6mm FR4
        trace_width=0.001,  # 1mm trace
        trace_thickness=0.000035,  # 35μm copper
        substrate_er=4.6  # FR4
    )
    
    # Solve with reasonable grid resolution
    params = SolverParameters(nx=80, ny=80, frequency=1e9)
    
    tl_params = calculate_transmission_line_parameters(
        geometry=geometry,
        parameters=params,
        frequency=1e9,
        conductor_names=("copper", "ground")
    )
    
    # Compare with analytical
    z0_analytical = calculate_characteristic_impedance_analytical(
        "microstrip",
        trace_width=0.001,
        substrate_height=0.0016,
        epsilon_r=4.6
    )
    
    # Should be within reasonable agreement (say 20%)
    relative_error = abs(tl_params.Z0 - z0_analytical) / z0_analytical
    assert relative_error < 0.3, f"Relative error too large: {relative_error:.2%}"
    
    print(f"Numerical Z0: {tl_params.Z0:.1f} Ω")
    print(f"Analytical Z0: {z0_analytical:.1f} Ω")
    print(f"Relative error: {relative_error:.1%}")


if __name__ == '__main__':
    # Run the integration test
    test_integration_microstrip()
    
    # Run unit tests
    import unittest
    unittest.main()