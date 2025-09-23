# 2D_EM_solver
A 2D EM solver able to slice KiCAD and other layout types and give you EM data on the sliced area.

# Goal
## 2D EM Solver
The solver will work a lot like Polar si9000 transmission line field solver. The inputs are a two dimensional geometry describing the transmission line (which is almost always a PCB microstrip or stripline or otherwise planar geometry). The output of this program will be RLGC parameters, characteristic impedence, and other transmission line parameters.

## Slicer
The slicer will allow the user to "draw a line" across a portion of a layout. The layout will be in a gerber format or something similar, as in a top-down 2.5D layout. By "drawing a line", that line will slice through the layout and the cross section of that line through the layout will be displayed. The point of this is so that a cross section of a transmission line can be obtained. This way, the user can just draw a line through the transmission line in question and obtain a 2D cross sectional geometry. This geometry will be then fed into the 2D EM solver.

## Result
The user can have a 2.5D layout from KiCAD or gerbers etc, and make a cross section at will. This cross section will automatically be solved for transmission line parameters.
