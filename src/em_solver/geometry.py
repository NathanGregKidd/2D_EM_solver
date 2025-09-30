"""Geometry definitions for 2D transmission line cross-sections."""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class Material:
    """Material properties for electromagnetic analysis."""
    name: str
    epsilon_r: float  # Relative permittivity
    mu_r: float = 1.0  # Relative permeability
    sigma: float = 0.0  # Conductivity (S/m)
    
    @property
    def is_conductor(self) -> bool:
        """Check if material is a conductor (high conductivity)."""
        return self.sigma > 1e6  # Typical threshold for good conductors


@dataclass
class Rectangle:
    """Rectangular region in 2D geometry."""
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    material: Material
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside rectangle."""
        return (self.x_min <= x <= self.x_max and 
                self.y_min <= y <= self.y_max)
    
    @property
    def width(self) -> float:
        return self.x_max - self.x_min
    
    @property
    def height(self) -> float:
        return self.y_max - self.y_min
    
    @property
    def area(self) -> float:
        return self.width * self.height


class Geometry2D:
    """2D transmission line geometry definition."""
    
    def __init__(self, width: float, height: float, default_material: Material):
        """Initialize geometry with bounding box and default material.
        
        Args:
            width: Total width of the geometry
            height: Total height of the geometry  
            default_material: Default material (usually air/vacuum)
        """
        self.width = width
        self.height = height
        self.default_material = default_material
        self.regions: List[Rectangle] = []
        
    def add_rectangle(self, rect: Rectangle) -> None:
        """Add a rectangular region to the geometry."""
        # Validate rectangle is within bounds
        if (rect.x_min < 0 or rect.x_max > self.width or 
            rect.y_min < 0 or rect.y_max > self.height):
            raise ValueError("Rectangle extends outside geometry bounds")
        
        self.regions.append(rect)
    
    def get_material_at(self, x: float, y: float) -> Material:
        """Get material at given point."""
        # Check regions in reverse order (last added takes precedence)
        for rect in reversed(self.regions):
            if rect.contains_point(x, y):
                return rect.material
        
        return self.default_material
    
    def get_conductor_regions(self) -> List[Rectangle]:
        """Get all conductor regions."""
        return [rect for rect in self.regions if rect.material.is_conductor]


def create_microstrip_geometry(
    substrate_width: float,
    substrate_height: float,
    trace_width: float,
    trace_thickness: float,
    substrate_er: float = 4.6,
    conductor_name: str = "signal",
    ground_thickness: float = None
) -> Geometry2D:
    """Create a microstrip transmission line geometry.
    
    A microstrip consists of:
    - Ground plane conductor at the bottom
    - Substrate layer above the ground plane
    - Signal trace on top of the substrate
    - Air region above the trace
    
    Args:
        substrate_width: Width of the substrate
        substrate_height: Height of the substrate
        trace_width: Width of the trace conductor
        trace_thickness: Thickness of the trace
        substrate_er: Relative permittivity of substrate
        conductor_name: Name of signal conductor material
        ground_thickness: Thickness of ground plane (if None, uses trace_thickness)
    
    Returns:
        Geometry2D: Configured microstrip geometry
    """
    # Set default ground plane thickness
    if ground_thickness is None:
        ground_thickness = trace_thickness
    
    # Materials
    air = Material("air", epsilon_r=1.0)
    substrate = Material("substrate", epsilon_r=substrate_er)
    signal_conductor = Material(conductor_name, epsilon_r=1.0, sigma=5.8e7)  # Copper
    ground_conductor = Material("ground", epsilon_r=1.0, sigma=5.8e7)  # Copper ground plane
    
    # Create geometry with air as default
    # Layout from bottom to top: ground plane -> substrate -> trace -> air
    total_height = ground_thickness + substrate_height + trace_thickness + substrate_height  # Air above
    geom = Geometry2D(substrate_width, total_height, air)
    
    # Add ground plane at the bottom (full width)
    ground_rect = Rectangle(
        x_min=0, x_max=substrate_width,
        y_min=0, y_max=ground_thickness,
        material=ground_conductor
    )
    geom.add_rectangle(ground_rect)
    
    # Add substrate above ground plane
    substrate_rect = Rectangle(
        x_min=0, x_max=substrate_width,
        y_min=ground_thickness, y_max=ground_thickness + substrate_height,
        material=substrate
    )
    geom.add_rectangle(substrate_rect)
    
    # Add signal trace on top of substrate (centered horizontally)
    trace_x_center = substrate_width / 2
    trace_y_bottom = ground_thickness + substrate_height
    trace_rect = Rectangle(
        x_min=trace_x_center - trace_width/2,
        x_max=trace_x_center + trace_width/2,
        y_min=trace_y_bottom,
        y_max=trace_y_bottom + trace_thickness,
        material=signal_conductor
    )
    geom.add_rectangle(trace_rect)
    
    return geom


def create_stripline_geometry(
    substrate_width: float,
    substrate_height: float,
    trace_width: float,
    trace_thickness: float,
    substrate_er: float = 4.6,
    conductor_name: str = "copper"
) -> Geometry2D:
    """Create a stripline transmission line geometry.
    
    Args:
        substrate_width: Width of the substrate
        substrate_height: Height of the substrate (between ground planes)
        trace_width: Width of the trace conductor
        trace_thickness: Thickness of the trace
        substrate_er: Relative permittivity of substrate
        conductor_name: Name of conductor material
    
    Returns:
        Geometry2D: Configured stripline geometry
    """
    # Materials
    substrate = Material("substrate", epsilon_r=substrate_er)
    conductor = Material(conductor_name, epsilon_r=1.0, sigma=5.8e7)  # Copper
    
    # Create geometry with substrate as default
    geom = Geometry2D(substrate_width, substrate_height, substrate)
    
    # Add trace (centered both horizontally and vertically)
    trace_x_center = substrate_width / 2
    trace_y_center = substrate_height / 2
    trace_rect = Rectangle(
        x_min=trace_x_center - trace_width/2,
        x_max=trace_x_center + trace_width/2,
        y_min=trace_y_center - trace_thickness/2,
        y_max=trace_y_center + trace_thickness/2,
        material=conductor
    )
    geom.add_rectangle(trace_rect)
    
    return geom