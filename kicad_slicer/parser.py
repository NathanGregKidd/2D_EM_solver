"""
KiCad PCB file parser module.
Handles parsing of .kicad_pcb files in S-expression format.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Point:
    """Represents a 2D point with x, y coordinates."""
    x: float
    y: float
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)


@dataclass
class Layer:
    """Represents a PCB layer."""
    name: str
    id: int
    type: str
    thickness: float = 0.0  # in mm
    z_position: float = 0.0  # in mm


@dataclass
class Track:
    """Represents a PCB track."""
    start: Point
    end: Point
    width: float
    layer: str
    net: int = 0


@dataclass
class Via:
    """Represents a PCB via."""
    position: Point
    size: float
    drill: float
    layers: List[str]
    net: int = 0


@dataclass
class Pad:
    """Represents a PCB pad."""
    position: Point
    size: Point  # width, height
    shape: str
    layers: List[str]
    net: int = 0
    drill: Optional[float] = None


class SExpressionParser:
    """Parser for S-expression format used by KiCad."""
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        
    def parse(self) -> List[Any]:
        """Parse S-expression text into nested lists."""
        result = []
        while self.pos < len(self.text):
            token = self.parse_token()
            if token is not None:
                result.append(token)
        return result
    
    def parse_token(self) -> Any:
        """Parse a single token or expression."""
        self.skip_whitespace()
        if self.pos >= len(self.text):
            return None
            
        if self.text[self.pos] == '(':
            return self.parse_list()
        elif self.text[self.pos] == '"':
            return self.parse_quoted_string()
        else:
            return self.parse_atom()
    
    def parse_list(self) -> List[Any]:
        """Parse a list expression."""
        self.pos += 1  # skip '('
        result = []
        
        while self.pos < len(self.text):
            self.skip_whitespace()
            if self.pos >= len(self.text):
                break
            if self.text[self.pos] == ')':
                self.pos += 1
                break
            token = self.parse_token()
            if token is not None:
                result.append(token)
                
        return result
    
    def parse_quoted_string(self) -> str:
        """Parse a quoted string."""
        self.pos += 1  # skip '"'
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            if self.text[self.pos] == '\\':
                self.pos += 2  # skip escaped character
            else:
                self.pos += 1
        result = self.text[start:self.pos]
        if self.pos < len(self.text):
            self.pos += 1  # skip closing '"'
        return result
    
    def parse_atom(self) -> Any:
        """Parse an atom (number or string)."""
        start = self.pos
        while (self.pos < len(self.text) and 
               self.text[self.pos] not in ' \t\n\r()'):
            self.pos += 1
        
        token = self.text[start:self.pos]
        
        # Try to parse as number
        try:
            if '.' in token:
                return float(token)
            else:
                return int(token)
        except ValueError:
            return token
    
    def skip_whitespace(self):
        """Skip whitespace and comments."""
        while self.pos < len(self.text):
            if self.text[self.pos] in ' \t\n\r':
                self.pos += 1
            elif self.text[self.pos:self.pos+2] == '/*':
                # Skip block comment
                self.pos += 2
                while self.pos < len(self.text) - 1:
                    if self.text[self.pos:self.pos+2] == '*/':
                        self.pos += 2
                        break
                    self.pos += 1
            else:
                break


class KiCadParser:
    """Main KiCad PCB file parser."""
    
    def __init__(self):
        self.layers: Dict[str, Layer] = {}
        self.tracks: List[Track] = []
        self.vias: List[Via] = []
        self.pads: List[Pad] = []
        self.board_bounds: Optional[Tuple[Point, Point]] = None
        
    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """Parse a KiCad PCB file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> Dict[str, Any]:
        """Parse KiCad PCB file content."""
        parser = SExpressionParser(content)
        data = parser.parse()
        
        if not data or data[0][0] != 'kicad_pcb':
            raise ValueError("Invalid KiCad PCB file format")
        
        pcb_data = data[0]
        self._parse_pcb_data(pcb_data)
        
        return {
            'layers': self.layers,
            'tracks': self.tracks,
            'vias': self.vias,
            'pads': self.pads,
            'board_bounds': self.board_bounds
        }
    
    def _parse_pcb_data(self, pcb_data: List[Any]):
        """Parse the main PCB data structure."""
        for item in pcb_data[1:]:  # Skip 'kicad_pcb' header
            if isinstance(item, list) and len(item) > 0:
                keyword = item[0]
                
                if keyword == 'layers':
                    self._parse_layers(item)
                elif keyword == 'segment':
                    self._parse_track(item)
                elif keyword == 'via':
                    self._parse_via(item)
                elif keyword == 'pad':
                    self._parse_pad(item)
                elif keyword == 'gr_line':
                    self._parse_graphic_line(item)
    
    def _parse_layers(self, layers_data: List[Any]):
        """Parse layer definitions."""
        for layer_item in layers_data[1:]:
            if isinstance(layer_item, list) and len(layer_item) >= 3:
                layer_id = layer_item[0]
                layer_name = layer_item[1]
                layer_type = layer_item[2] if len(layer_item) > 2 else 'signal'
                
                self.layers[layer_name] = Layer(
                    name=layer_name,
                    id=layer_id,
                    type=layer_type
                )
    
    def _parse_track(self, track_data: List[Any]):
        """Parse a track (segment) definition."""
        start_point = None
        end_point = None
        width = 0.0
        layer = ""
        net = 0
        
        for item in track_data[1:]:
            if isinstance(item, list) and len(item) >= 2:
                keyword = item[0]
                if keyword == 'start':
                    start_point = Point(float(item[1]), float(item[2]))
                elif keyword == 'end':
                    end_point = Point(float(item[1]), float(item[2]))
                elif keyword == 'width':
                    width = float(item[1])
                elif keyword == 'layer':
                    layer = item[1]
                elif keyword == 'net':
                    net = int(item[1])
        
        if start_point and end_point:
            track = Track(
                start=start_point,
                end=end_point,
                width=width,
                layer=layer,
                net=net
            )
            self.tracks.append(track)
    
    def _parse_via(self, via_data: List[Any]):
        """Parse a via definition."""
        position = None
        size = 0.0
        drill = 0.0
        layers = []
        net = 0
        
        for item in via_data[1:]:
            if isinstance(item, list) and len(item) >= 2:
                keyword = item[0]
                if keyword == 'at':
                    position = Point(float(item[1]), float(item[2]))
                elif keyword == 'size':
                    size = float(item[1])
                elif keyword == 'drill':
                    drill = float(item[1])
                elif keyword == 'layers':
                    layers = [str(layer) for layer in item[1:]]
                elif keyword == 'net':
                    net = int(item[1])
        
        if position:
            via = Via(
                position=position,
                size=size,
                drill=drill,
                layers=layers,
                net=net
            )
            self.vias.append(via)
    
    def _parse_pad(self, pad_data: List[Any]):
        """Parse a pad definition."""
        position = None
        size = None
        shape = "circle"
        layers = []
        net = 0
        drill = None
        
        for item in pad_data[1:]:
            if isinstance(item, list) and len(item) >= 2:
                keyword = item[0]
                if keyword == 'at':
                    position = Point(float(item[1]), float(item[2]))
                elif keyword == 'size':
                    size = Point(float(item[1]), float(item[2]))
                elif keyword == 'shape' and len(item) > 1:
                    shape = str(item[1])
                elif keyword == 'layers':
                    layers = [str(layer) for layer in item[1:]]
                elif keyword == 'net':
                    net = int(item[1])
                elif keyword == 'drill':
                    drill = float(item[1])
        
        if position and size:
            pad = Pad(
                position=position,
                size=size,
                shape=shape,
                layers=layers,
                net=net,
                drill=drill
            )
            self.pads.append(pad)
    
    def _parse_graphic_line(self, line_data: List[Any]):
        """Parse graphic line (board outline, etc.)."""
        # For now, we'll skip graphic lines as they're mainly for visual reference
        # In a full implementation, these could be used for board outline detection
        pass


def parse_kicad_pcb(filepath: str) -> Dict[str, Any]:
    """Convenience function to parse a KiCad PCB file."""
    parser = KiCadParser()
    return parser.parse_file(filepath)