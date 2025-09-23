"""
2D Cross-section slicer for KiCad layouts.
This module handles creating cross-sections through PCB layouts.
"""

import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np

from .parser import Point, Track, Via, Pad, Layer


@dataclass
class CrossSectionElement:
    """Represents an element in a cross-section."""
    x_start: float
    x_end: float
    z_start: float
    z_end: float
    material: str
    layer_name: str
    element_type: str  # 'track', 'via', 'pad', 'substrate'
    net: int = 0


@dataclass
class SliceLine:
    """Represents a line for slicing through the PCB."""
    start: Point
    end: Point
    
    @property
    def length(self) -> float:
        """Calculate the length of the slice line."""
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        return math.sqrt(dx * dx + dy * dy)
    
    @property
    def angle(self) -> float:
        """Calculate the angle of the slice line in radians."""
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        return math.atan2(dy, dx)


class CrossSectionSlicer:
    """Creates 2D cross-sections from 3D PCB data."""
    
    def __init__(self, pcb_data: Dict[str, Any]):
        self.pcb_data = pcb_data
        self.layers = pcb_data.get('layers', {})
        self.tracks = pcb_data.get('tracks', [])
        self.vias = pcb_data.get('vias', [])
        self.pads = pcb_data.get('pads', [])
        
        # Standard PCB layer stack-up (simplified)
        self.layer_stack = self._build_layer_stack()
    
    def _build_layer_stack(self) -> Dict[str, Dict[str, float]]:
        """Build a simplified layer stack-up with Z positions and thicknesses."""
        # This is a simplified 4-layer PCB stack-up
        # In a real implementation, this would be parsed from the KiCad file
        return {
            'F.Cu': {'z_position': 1.5, 'thickness': 0.035, 'material': 'copper'},
            'In1.Cu': {'z_position': 0.5, 'thickness': 0.035, 'material': 'copper'},
            'In2.Cu': {'z_position': -0.5, 'thickness': 0.035, 'material': 'copper'},
            'B.Cu': {'z_position': -1.5, 'thickness': 0.035, 'material': 'copper'},
            'dielectric_1': {'z_position': 1.0, 'thickness': 1.0, 'material': 'fr4'},
            'dielectric_2': {'z_position': 0.0, 'thickness': 1.0, 'material': 'fr4'},
            'dielectric_3': {'z_position': -1.0, 'thickness': 1.0, 'material': 'fr4'},
        }
    
    def create_cross_section(self, slice_line: SliceLine, 
                           slice_width: float = 0.1) -> List[CrossSectionElement]:
        """
        Create a 2D cross-section along the specified line.
        
        Args:
            slice_line: Line along which to create the cross-section
            slice_width: Width of the slice (tolerance for selecting elements)
        
        Returns:
            List of cross-section elements
        """
        elements = []
        
        # Add substrate/dielectric elements first
        elements.extend(self._slice_substrate(slice_line))
        
        # Process tracks
        for track in self.tracks:
            element = self._slice_track(track, slice_line, slice_width)
            if element:
                elements.append(element)
        
        # Process vias
        for via in self.vias:
            element = self._slice_via(via, slice_line, slice_width)
            if element:
                elements.append(element)
        
        # Process pads
        for pad in self.pads:
            element = self._slice_pad(pad, slice_line, slice_width)
            if element:
                elements.append(element)
        
        return sorted(elements, key=lambda e: e.x_start)
    
    def _slice_substrate(self, slice_line: SliceLine) -> List[CrossSectionElement]:
        """Create substrate/dielectric elements for the cross-section."""
        elements = []
        
        # Create dielectric elements spanning the entire cross-section width
        cross_section_width = slice_line.length
        
        for layer_name, props in self.layer_stack.items():
            if props['material'] == 'fr4':
                z_center = props['z_position']
                thickness = props['thickness']
                
                element = CrossSectionElement(
                    x_start=0.0,
                    x_end=cross_section_width,
                    z_start=z_center - thickness/2,
                    z_end=z_center + thickness/2,
                    material='fr4',
                    layer_name=layer_name,
                    element_type='substrate'
                )
                elements.append(element)
        
        return elements
    
    def _slice_track(self, track: Track, slice_line: SliceLine, 
                    slice_width: float) -> Optional[CrossSectionElement]:
        """Create cross-section element from a track if it intersects the slice line."""
        # Check if track intersects with the slice line
        intersection = self._line_intersection(
            track.start, track.end, slice_line.start, slice_line.end, slice_width
        )
        
        if not intersection:
            return None
        
        # Calculate position along slice line
        x_pos = self._distance_along_line(slice_line.start, intersection, slice_line)
        
        # Get layer properties
        if track.layer not in self.layer_stack:
            return None
            
        layer_props = self.layer_stack[track.layer]
        z_center = layer_props['z_position']
        thickness = layer_props['thickness']
        
        return CrossSectionElement(
            x_start=x_pos - track.width/2,
            x_end=x_pos + track.width/2,
            z_start=z_center - thickness/2,
            z_end=z_center + thickness/2,
            material='copper',
            layer_name=track.layer,
            element_type='track',
            net=track.net
        )
    
    def _slice_via(self, via: Via, slice_line: SliceLine, 
                  slice_width: float) -> Optional[CrossSectionElement]:
        """Create cross-section element from a via if it intersects the slice line."""
        # Check if via is close enough to the slice line
        distance = self._point_to_line_distance(via.position, slice_line.start, slice_line.end)
        
        if distance > slice_width:
            return None
        
        # Calculate position along slice line
        closest_point = self._closest_point_on_line(via.position, slice_line.start, slice_line.end)
        x_pos = self._distance_along_line(slice_line.start, closest_point, slice_line)
        
        # Vias span multiple layers - create element from top to bottom copper layer
        z_top = max(self.layer_stack[layer]['z_position'] + self.layer_stack[layer]['thickness']/2 
                   for layer in via.layers if layer in self.layer_stack)
        z_bottom = min(self.layer_stack[layer]['z_position'] - self.layer_stack[layer]['thickness']/2 
                      for layer in via.layers if layer in self.layer_stack)
        
        return CrossSectionElement(
            x_start=x_pos - via.size/2,
            x_end=x_pos + via.size/2,
            z_start=z_bottom,
            z_end=z_top,
            material='copper',
            layer_name='via',
            element_type='via',
            net=via.net
        )
    
    def _slice_pad(self, pad: Pad, slice_line: SliceLine, 
                  slice_width: float) -> Optional[CrossSectionElement]:
        """Create cross-section element from a pad if it intersects the slice line."""
        # Check if pad is close enough to the slice line
        distance = self._point_to_line_distance(pad.position, slice_line.start, slice_line.end)
        
        # Use pad size to determine if it intersects
        max_pad_dimension = max(pad.size.x, pad.size.y)
        if distance > slice_width + max_pad_dimension/2:
            return None
        
        # Calculate position along slice line
        closest_point = self._closest_point_on_line(pad.position, slice_line.start, slice_line.end)
        x_pos = self._distance_along_line(slice_line.start, closest_point, slice_line)
        
        # Use the first layer the pad is on
        if not pad.layers:
            return None
            
        layer_name = pad.layers[0]
        if layer_name not in self.layer_stack:
            return None
            
        layer_props = self.layer_stack[layer_name]
        z_center = layer_props['z_position']
        thickness = layer_props['thickness']
        
        # Determine pad width in cross-section (simplified)
        pad_width = min(pad.size.x, pad.size.y)  # Use smaller dimension as width
        
        return CrossSectionElement(
            x_start=x_pos - pad_width/2,
            x_end=x_pos + pad_width/2,
            z_start=z_center - thickness/2,
            z_end=z_center + thickness/2,
            material='copper',
            layer_name=layer_name,
            element_type='pad',
            net=pad.net
        )
    
    def _line_intersection(self, p1: Point, p2: Point, p3: Point, p4: Point, 
                          tolerance: float) -> Optional[Point]:
        """Find intersection point between two line segments with tolerance."""
        # Calculate line intersection using parametric form
        dx1, dy1 = p2.x - p1.x, p2.y - p1.y
        dx2, dy2 = p4.x - p3.x, p4.y - p3.y
        dx3, dy3 = p1.x - p3.x, p1.y - p3.y
        
        denominator = dx1 * dy2 - dy1 * dx2
        if abs(denominator) < 1e-10:  # Lines are parallel
            # Check if lines are close enough to be considered intersecting
            dist = self._point_to_line_distance(p1, p3, p4)
            if dist <= tolerance:
                # Return midpoint of the closest approach
                return self._closest_point_on_line(p1, p3, p4)
            return None
        
        t1 = (dx2 * dy3 - dy2 * dx3) / denominator
        t2 = (dx1 * dy3 - dy1 * dx3) / denominator
        
        # Check if intersection is within both line segments
        if 0 <= t1 <= 1 and 0 <= t2 <= 1:
            return Point(p1.x + t1 * dx1, p1.y + t1 * dy1)
        
        return None
    
    def _point_to_line_distance(self, point: Point, line_start: Point, line_end: Point) -> float:
        """Calculate the shortest distance from a point to a line segment."""
        dx = line_end.x - line_start.x
        dy = line_end.y - line_start.y
        
        if dx == 0 and dy == 0:
            # Line is a point
            return math.sqrt((point.x - line_start.x)**2 + (point.y - line_start.y)**2)
        
        # Calculate the parameter t for the closest point on the line
        t = ((point.x - line_start.x) * dx + (point.y - line_start.y) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))  # Clamp to line segment
        
        # Find the closest point on the line segment
        closest_x = line_start.x + t * dx
        closest_y = line_start.y + t * dy
        
        # Return distance to closest point
        return math.sqrt((point.x - closest_x)**2 + (point.y - closest_y)**2)
    
    def _closest_point_on_line(self, point: Point, line_start: Point, line_end: Point) -> Point:
        """Find the closest point on a line segment to a given point."""
        dx = line_end.x - line_start.x
        dy = line_end.y - line_start.y
        
        if dx == 0 and dy == 0:
            return line_start
        
        t = ((point.x - line_start.x) * dx + (point.y - line_start.y) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))  # Clamp to line segment
        
        return Point(line_start.x + t * dx, line_start.y + t * dy)
    
    def _distance_along_line(self, line_start: Point, point: Point, slice_line: SliceLine) -> float:
        """Calculate distance along the slice line from start to point."""
        dx = point.x - line_start.x
        dy = point.y - line_start.y
        return math.sqrt(dx * dx + dy * dy)


def create_cross_section(pcb_data: Dict[str, Any], start_point: Tuple[float, float], 
                        end_point: Tuple[float, float], 
                        slice_width: float = 0.1) -> List[CrossSectionElement]:
    """
    Convenience function to create a cross-section from PCB data.
    
    Args:
        pcb_data: Parsed PCB data from KiCadParser
        start_point: Starting point of the slice line (x, y)
        end_point: Ending point of the slice line (x, y)
        slice_width: Width tolerance for the slice
    
    Returns:
        List of cross-section elements
    """
    slicer = CrossSectionSlicer(pcb_data)
    slice_line = SliceLine(
        start=Point(start_point[0], start_point[1]),
        end=Point(end_point[0], end_point[1])
    )
    return slicer.create_cross_section(slice_line, slice_width)