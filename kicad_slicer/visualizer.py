"""
Visualization module for cross-sections.
Creates plots and diagrams of PCB cross-sections.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from .slicer import CrossSectionElement


class CrossSectionVisualizer:
    """Visualizes 2D cross-sections of PCB layouts."""
    
    # Material colors for visualization
    MATERIAL_COLORS = {
        'copper': '#B87333',
        'fr4': '#90EE90',
        'substrate': '#90EE90',
        'air': '#E6F3FF'
    }
    
    # Layer colors for different net visualization
    NET_COLORS = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
        '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
    ]
    
    def __init__(self):
        self.fig = None
        self.ax = None
    
    def plot_cross_section(self, elements: List[CrossSectionElement], 
                          title: str = "PCB Cross Section",
                          figsize: Tuple[int, int] = (12, 8),
                          show_nets: bool = True,
                          show_grid: bool = True) -> plt.Figure:
        """
        Plot a cross-section with all its elements.
        
        Args:
            elements: List of cross-section elements to plot
            title: Title for the plot
            figsize: Figure size (width, height)
            show_nets: Whether to color-code elements by net
            show_grid: Whether to show grid lines
        
        Returns:
            The matplotlib figure object
        """
        self.fig, self.ax = plt.subplots(1, 1, figsize=figsize)
        
        # Calculate plot bounds
        if not elements:
            self.ax.set_xlim(0, 10)
            self.ax.set_ylim(-2, 2)
        else:
            x_min = min(elem.x_start for elem in elements)
            x_max = max(elem.x_end for elem in elements)
            z_min = min(elem.z_start for elem in elements)
            z_max = max(elem.z_end for elem in elements)
            
            # Add some padding
            x_padding = (x_max - x_min) * 0.1 if x_max > x_min else 1
            z_padding = (z_max - z_min) * 0.1 if z_max > z_min else 1
            
            self.ax.set_xlim(x_min - x_padding, x_max + x_padding)
            self.ax.set_ylim(z_min - z_padding, z_max + z_padding)
        
        # Draw elements
        net_assignments = {}
        net_counter = 0
        
        for element in elements:
            color = self._get_element_color(element, show_nets, net_assignments, net_counter)
            if show_nets and element.net > 0 and element.net not in net_assignments:
                net_assignments[element.net] = net_counter % len(self.NET_COLORS)
                net_counter += 1
            
            self._draw_element(element, color)
        
        # Customize plot
        self.ax.set_xlabel('Distance along slice (mm)', fontsize=12)
        self.ax.set_ylabel('Height (mm)', fontsize=12)
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        
        if show_grid:
            self.ax.grid(True, alpha=0.3)
        
        # Add legend
        self._add_legend(elements, show_nets, net_assignments)
        
        # Set aspect ratio to be equal for proper visualization
        self.ax.set_aspect('equal', adjustable='box')
        
        plt.tight_layout()
        return self.fig
    
    def _get_element_color(self, element: CrossSectionElement, show_nets: bool,
                          net_assignments: Dict[int, int], net_counter: int) -> str:
        """Determine the color for an element based on material or net."""
        if show_nets and element.net > 0 and element.material == 'copper':
            if element.net in net_assignments:
                return self.NET_COLORS[net_assignments[element.net]]
            else:
                return self.NET_COLORS[net_counter % len(self.NET_COLORS)]
        else:
            return self.MATERIAL_COLORS.get(element.material, '#CCCCCC')
    
    def _draw_element(self, element: CrossSectionElement, color: str):
        """Draw a single cross-section element."""
        width = element.x_end - element.x_start
        height = element.z_end - element.z_start
        
        rect = patches.Rectangle(
            (element.x_start, element.z_start),
            width, height,
            facecolor=color,
            edgecolor='black',
            linewidth=0.5,
            alpha=0.8 if element.material == 'fr4' else 1.0
        )
        
        self.ax.add_patch(rect)
        
        # Add text label for important elements
        if element.element_type in ['track', 'via', 'pad'] and width > 0.5:
            center_x = element.x_start + width / 2
            center_z = element.z_start + height / 2
            
            label = f"{element.element_type}"
            if element.net > 0:
                label += f"\nNet {element.net}"
            
            self.ax.text(center_x, center_z, label, 
                        ha='center', va='center', fontsize=8,
                        color='white' if element.material == 'copper' else 'black')
    
    def _add_legend(self, elements: List[CrossSectionElement], show_nets: bool,
                   net_assignments: Dict[int, int]):
        """Add a legend to the plot."""
        legend_elements = []
        
        # Add material legend
        materials = set(elem.material for elem in elements)
        for material in materials:
            color = self.MATERIAL_COLORS.get(material, '#CCCCCC')
            legend_elements.append(
                patches.Patch(color=color, label=material.capitalize())
            )
        
        # Add net legend if showing nets
        if show_nets and net_assignments:
            legend_elements.append(patches.Patch(color='none', label='Nets:'))
            for net, color_idx in sorted(net_assignments.items()):
                color = self.NET_COLORS[color_idx]
                legend_elements.append(
                    patches.Patch(color=color, label=f'Net {net}')
                )
        
        if legend_elements:
            self.ax.legend(handles=legend_elements, loc='upper right', 
                          bbox_to_anchor=(1.15, 1))
    
    def save_plot(self, filename: str, dpi: int = 300):
        """Save the current plot to a file."""
        if self.fig:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    
    def show_plot(self):
        """Display the current plot."""
        if self.fig:
            plt.show()


def plot_cross_section(elements: List[CrossSectionElement], 
                      title: str = "PCB Cross Section",
                      figsize: Tuple[int, int] = (12, 8),
                      show_nets: bool = True,
                      show_grid: bool = True,
                      save_path: Optional[str] = None) -> plt.Figure:
    """
    Convenience function to plot a cross-section.
    
    Args:
        elements: List of cross-section elements to plot
        title: Title for the plot
        figsize: Figure size (width, height)
        show_nets: Whether to color-code elements by net
        show_grid: Whether to show grid lines
        save_path: Optional path to save the plot
    
    Returns:
        The matplotlib figure object
    """
    visualizer = CrossSectionVisualizer()
    fig = visualizer.plot_cross_section(elements, title, figsize, show_nets, show_grid)
    
    if save_path:
        visualizer.save_plot(save_path)
    
    return fig


def create_layer_stack_diagram(layer_stack: Dict[str, Dict[str, float]], 
                             figsize: Tuple[int, int] = (8, 6)) -> plt.Figure:
    """
    Create a diagram showing the PCB layer stack-up.
    
    Args:
        layer_stack: Dictionary of layer properties
        figsize: Figure size (width, height)
    
    Returns:
        The matplotlib figure object
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    
    # Sort layers by Z position (top to bottom)
    sorted_layers = sorted(layer_stack.items(), 
                          key=lambda x: x[1]['z_position'], reverse=True)
    
    y_pos = 0
    for layer_name, props in sorted_layers:
        thickness = props['thickness']
        material = props['material']
        color = CrossSectionVisualizer.MATERIAL_COLORS.get(material, '#CCCCCC')
        
        # Draw layer rectangle
        rect = patches.Rectangle(
            (0, y_pos - thickness), 2, thickness,
            facecolor=color, edgecolor='black', linewidth=1
        )
        ax.add_patch(rect)
        
        # Add layer label
        ax.text(2.1, y_pos - thickness/2, f"{layer_name}\n{thickness:.3f}mm", 
               va='center', fontsize=10)
        
        y_pos -= thickness
    
    ax.set_xlim(-0.5, 4)
    ax.set_ylim(y_pos - 0.5, 0.5)
    ax.set_aspect('equal')
    ax.set_title('PCB Layer Stack-up', fontsize=14, fontweight='bold')
    ax.set_xlabel('Width', fontsize=12)
    ax.set_ylabel('Height (mm)', fontsize=12)
    
    # Remove x-axis ticks as width is not meaningful
    ax.set_xticks([])
    
    plt.tight_layout()
    return fig