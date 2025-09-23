"""
Basic tests for the KiCad parser and slicer functionality.
"""

import unittest
from pathlib import Path
import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kicad_slicer.parser import parse_kicad_pcb, KiCadParser, Point
from kicad_slicer.slicer import create_cross_section, SliceLine, CrossSectionSlicer


class TestKiCadParser(unittest.TestCase):
    """Test the KiCad parser functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_file = Path(__file__).parent.parent / "examples" / "test_board.kicad_pcb"
        
    def test_parse_file_exists(self):
        """Test that the test file exists."""
        self.assertTrue(self.test_file.exists(), f"Test file not found: {self.test_file}")
    
    def test_parse_basic_structure(self):
        """Test basic parsing of the KiCad file."""
        pcb_data = parse_kicad_pcb(str(self.test_file))
        
        # Check that basic structure exists
        self.assertIn('layers', pcb_data)
        self.assertIn('tracks', pcb_data)
        self.assertIn('vias', pcb_data)
        self.assertIn('pads', pcb_data)
    
    def test_parse_layers(self):
        """Test parsing of layer definitions."""
        pcb_data = parse_kicad_pcb(str(self.test_file))
        layers = pcb_data['layers']
        
        # Should have at least the copper layers
        expected_layers = ['F.Cu', 'B.Cu']
        for layer in expected_layers:
            self.assertIn(layer, layers)
            self.assertEqual(layers[layer].name, layer)
    
    def test_parse_tracks(self):
        """Test parsing of track segments."""
        pcb_data = parse_kicad_pcb(str(self.test_file))
        tracks = pcb_data['tracks']
        
        # Should have multiple tracks
        self.assertGreater(len(tracks), 0)
        
        # Check first track properties
        track = tracks[0]
        self.assertIsInstance(track.start, Point)
        self.assertIsInstance(track.end, Point)
        self.assertGreater(track.width, 0)
        self.assertTrue(track.layer)
    
    def test_parse_vias(self):
        """Test parsing of vias."""
        pcb_data = parse_kicad_pcb(str(self.test_file))
        vias = pcb_data['vias']
        
        # Should have vias in test file
        self.assertGreater(len(vias), 0)
        
        # Check via properties
        via = vias[0]
        self.assertIsInstance(via.position, Point)
        self.assertGreater(via.size, 0)
        self.assertGreater(via.drill, 0)
        self.assertIsInstance(via.layers, list)


class TestCrossSectionSlicer(unittest.TestCase):
    """Test the cross-section slicer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_file = Path(__file__).parent.parent / "examples" / "test_board.kicad_pcb"
        self.pcb_data = parse_kicad_pcb(str(self.test_file))
    
    def test_create_cross_section(self):
        """Test basic cross-section creation."""
        # Create a cross-section that should intersect some tracks
        elements = create_cross_section(
            self.pcb_data,
            start_point=(0, 10),  # Horizontal line through y=10
            end_point=(30, 10),
            slice_width=0.5
        )
        
        # Should have some elements
        self.assertGreater(len(elements), 0)
        
        # Should have substrate elements
        substrate_elements = [e for e in elements if e.element_type == 'substrate']
        self.assertGreater(len(substrate_elements), 0)
    
    def test_slice_line_properties(self):
        """Test SliceLine properties."""
        line = SliceLine(Point(0, 0), Point(3, 4))
        
        # Test length calculation (3-4-5 triangle)
        self.assertAlmostEqual(line.length, 5.0, places=5)
        
        # Test angle calculation
        expected_angle = 0.9272952180016122  # arctan(4/3)
        self.assertAlmostEqual(line.angle, expected_angle, places=5)
    
    def test_cross_section_elements(self):
        """Test cross-section element properties."""
        elements = create_cross_section(
            self.pcb_data,
            start_point=(0, 10),
            end_point=(30, 10),
            slice_width=0.5
        )
        
        for element in elements:
            # All elements should have valid dimensions
            self.assertLessEqual(element.x_start, element.x_end)
            self.assertLessEqual(element.z_start, element.z_end)
            
            # Should have material and layer information
            self.assertTrue(element.material)
            self.assertTrue(element.layer_name)
            self.assertTrue(element.element_type)


class TestPointClass(unittest.TestCase):
    """Test the Point class functionality."""
    
    def test_point_operations(self):
        """Test Point arithmetic operations."""
        p1 = Point(1, 2)
        p2 = Point(3, 4)
        
        # Test addition
        p3 = p1 + p2
        self.assertEqual(p3.x, 4)
        self.assertEqual(p3.y, 6)
        
        # Test subtraction
        p4 = p2 - p1
        self.assertEqual(p4.x, 2)
        self.assertEqual(p4.y, 2)
        
        # Test multiplication
        p5 = p1 * 2
        self.assertEqual(p5.x, 2)
        self.assertEqual(p5.y, 4)


if __name__ == '__main__':
    # Run the tests
    unittest.main()