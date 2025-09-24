"""Visualization tools for 2D electromagnetic field solutions."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as MPLRectangle
from matplotlib.colors import LogNorm
from typing import Optional, Tuple, List
import matplotlib.patches as patches

from .solver import FieldSolution
from .geometry import Geometry2D, Rectangle


def plot_geometry(geometry: Geometry2D, ax: Optional[plt.Axes] = None, 
                 show_materials: bool = True) -> plt.Axes:
    """Plot the 2D geometry showing material regions.
    
    Args:
        geometry: 2D geometry to plot
        ax: Matplotlib axes (creates new figure if None)
        show_materials: Whether to show material labels
        
    Returns:
        plt.Axes: The axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # Define colors for different material types
    colors = {
        'conductor': 'gold',
        'dielectric': 'lightblue',
        'air': 'white'
    }
    
    # Plot background (default material)
    bg_color = 'white' if geometry.default_material.epsilon_r == 1.0 else 'lightblue'
    background = MPLRectangle((0, 0), geometry.width, geometry.height, 
                             facecolor=bg_color, edgecolor='black', linewidth=1)
    ax.add_patch(background)
    
    # Plot each region
    for i, region in enumerate(geometry.regions):
        # Determine color based on material properties
        if region.material.is_conductor:
            color = colors['conductor']
            label = f"Conductor ({region.material.name})"
        elif region.material.epsilon_r > 1.0:
            color = colors['dielectric']
            label = f"Dielectric (εᵣ={region.material.epsilon_r:.1f})"
        else:
            color = colors['air']
            label = f"Air ({region.material.name})"
        
        # Create rectangle patch
        rect = MPLRectangle(
            (region.x_min, region.y_min),
            region.width, region.height,
            facecolor=color, edgecolor='black', linewidth=1.5,
            alpha=0.8
        )
        ax.add_patch(rect)
        
        # Add material label if requested
        if show_materials:
            center_x = (region.x_min + region.x_max) / 2
            center_y = (region.y_min + region.y_max) / 2
            ax.text(center_x, center_y, region.material.name, 
                   ha='center', va='center', fontsize=8, weight='bold')
    
    ax.set_xlim(0, geometry.width)
    ax.set_ylim(0, geometry.height)
    ax.set_aspect('equal')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title('Geometry Cross-Section')
    ax.grid(True, alpha=0.3)
    
    return ax


def plot_potential(solution: FieldSolution, ax: Optional[plt.Axes] = None,
                  levels: int = 20, show_conductors: bool = True) -> plt.Axes:
    """Plot electric potential distribution.
    
    Args:
        solution: Field solution to plot
        ax: Matplotlib axes (creates new figure if None)
        levels: Number of contour levels
        show_conductors: Whether to overlay conductor regions
        
    Returns:
        plt.Axes: The axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create meshgrid for plotting
    X, Y = np.meshgrid(solution.x_grid, solution.y_grid)
    
    # Plot potential contours
    contour = ax.contourf(X, Y, solution.electric_potential, levels=levels, cmap='viridis')
    contour_lines = ax.contour(X, Y, solution.electric_potential, levels=levels, 
                              colors='white', alpha=0.5, linewidths=0.5)
    
    # Add colorbar
    cbar = plt.colorbar(contour, ax=ax)
    cbar.set_label('Electric Potential (V)')
    
    # Overlay conductor regions
    if show_conductors:
        for region in solution.geometry.get_conductor_regions():
            rect = MPLRectangle(
                (region.x_min, region.y_min),
                region.width, region.height,
                facecolor='none', edgecolor='red', linewidth=2
            )
            ax.add_patch(rect)
    
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title('Electric Potential Distribution')
    ax.set_aspect('equal')
    
    return ax


def plot_electric_field(solution: FieldSolution, ax: Optional[plt.Axes] = None,
                       component: str = 'magnitude', levels: int = 20,
                       show_vectors: bool = False, vector_scale: float = 1.0,
                       show_conductors: bool = True) -> plt.Axes:
    """Plot electric field distribution.
    
    Args:
        solution: Field solution to plot
        ax: Matplotlib axes (creates new figure if None)
        component: Which component to plot ('x', 'y', 'magnitude')
        levels: Number of contour levels
        show_vectors: Whether to show field vectors
        vector_scale: Scale factor for field vectors
        show_conductors: Whether to overlay conductor regions
        
    Returns:
        plt.Axes: The axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create meshgrid for plotting
    X, Y = np.meshgrid(solution.x_grid, solution.y_grid)
    
    # Select field component to plot
    if component == 'x':
        field_data = solution.electric_field_x
        title = 'Electric Field Ex Component'
        label = 'Ex (V/m)'
        cmap = 'RdBu_r'
    elif component == 'y':
        field_data = solution.electric_field_y
        title = 'Electric Field Ey Component'
        label = 'Ey (V/m)'
        cmap = 'RdBu_r'
    elif component == 'magnitude':
        field_data = solution.electric_field_magnitude
        title = 'Electric Field Magnitude'
        label = '|E| (V/m)'
        cmap = 'plasma'
    else:
        raise ValueError("Component must be 'x', 'y', or 'magnitude'")
    
    # Plot field contours
    # Use log scale for magnitude plots if there's a large dynamic range
    if component == 'magnitude' and np.max(field_data) / np.min(field_data[field_data > 0]) > 100:
        contour = ax.contourf(X, Y, field_data, levels=levels, cmap=cmap, norm=LogNorm())
    else:
        contour = ax.contourf(X, Y, field_data, levels=levels, cmap=cmap)
    
    # Add colorbar
    cbar = plt.colorbar(contour, ax=ax)
    cbar.set_label(label)
    
    # Overlay field vectors
    if show_vectors:
        # Subsample for vector plot
        stride = max(1, len(solution.x_grid) // 20)
        X_vec = X[::stride, ::stride]
        Y_vec = Y[::stride, ::stride]
        Ex_vec = solution.electric_field_x[::stride, ::stride]
        Ey_vec = solution.electric_field_y[::stride, ::stride]
        
        ax.quiver(X_vec, Y_vec, Ex_vec, Ey_vec, 
                 scale=vector_scale, alpha=0.7, color='white')
    
    # Overlay conductor regions
    if show_conductors:
        for region in solution.geometry.get_conductor_regions():
            rect = MPLRectangle(
                (region.x_min, region.y_min),
                region.width, region.height,
                facecolor='none', edgecolor='red', linewidth=2
            )
            ax.add_patch(rect)
    
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title(title)
    ax.set_aspect('equal')
    
    return ax


def plot_field_lines(solution: FieldSolution, ax: Optional[plt.Axes] = None,
                    density: float = 2.0, show_conductors: bool = True) -> plt.Axes:
    """Plot electric field lines.
    
    Args:
        solution: Field solution to plot
        ax: Matplotlib axes (creates new figure if None)
        density: Density of field lines
        show_conductors: Whether to overlay conductor regions
        
    Returns:
        plt.Axes: The axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create meshgrid for plotting
    X, Y = np.meshgrid(solution.x_grid, solution.y_grid)
    
    # Plot field lines (streamlines)
    ax.streamplot(X, Y, solution.electric_field_x, solution.electric_field_y,
                 density=density, color='blue', linewidth=1.0, arrowsize=1.5)
    
    # Overlay conductor regions
    if show_conductors:
        for region in solution.geometry.get_conductor_regions():
            rect = MPLRectangle(
                (region.x_min, region.y_min),
                region.width, region.height,
                facecolor='gold', edgecolor='red', linewidth=2, alpha=0.8
            )
            ax.add_patch(rect)
            
            # Add conductor label
            center_x = (region.x_min + region.x_max) / 2
            center_y = (region.y_min + region.y_max) / 2
            ax.text(center_x, center_y, region.material.name, 
                   ha='center', va='center', fontsize=8, weight='bold')
    
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title('Electric Field Lines')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    return ax


def create_complete_field_plot(solution: FieldSolution, figsize: Tuple[float, float] = (15, 10)) -> plt.Figure:
    """Create a comprehensive plot showing geometry, potential, and field.
    
    Args:
        solution: Field solution to plot
        figsize: Figure size
        
    Returns:
        plt.Figure: The complete figure
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('2D Electromagnetic Field Solution', fontsize=16)
    
    # Plot geometry
    plot_geometry(solution.geometry, axes[0, 0])
    
    # Plot potential
    plot_potential(solution, axes[0, 1])
    
    # Plot field magnitude
    plot_electric_field(solution, axes[1, 0], component='magnitude')
    
    # Plot field lines
    plot_field_lines(solution, axes[1, 1])
    
    plt.tight_layout()
    return fig


def save_field_plots(solution: FieldSolution, prefix: str = "field_solution") -> List[str]:
    """Save various field plots to files.
    
    Args:
        solution: Field solution to plot
        prefix: Prefix for output filenames
        
    Returns:
        List[str]: List of saved filenames
    """
    filenames = []
    
    # Complete field plot
    fig_complete = create_complete_field_plot(solution)
    filename_complete = f"{prefix}_complete.png"
    fig_complete.savefig(filename_complete, dpi=300, bbox_inches='tight')
    filenames.append(filename_complete)
    plt.close(fig_complete)
    
    # Individual plots
    plots = [
        ('geometry', lambda ax: plot_geometry(solution.geometry, ax)),
        ('potential', lambda ax: plot_potential(solution, ax)),
        ('field_magnitude', lambda ax: plot_electric_field(solution, ax, component='magnitude')),
        ('field_lines', lambda ax: plot_field_lines(solution, ax))
    ]
    
    for plot_name, plot_func in plots:
        fig, ax = plt.subplots(figsize=(8, 6))
        plot_func(ax)
        filename = f"{prefix}_{plot_name}.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        filenames.append(filename)
        plt.close(fig)
    
    return filenames