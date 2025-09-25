# Technical requirements
This document details the actual capabilities of the product.

## The Geometry Designer UI
The Geometry Designer UI provides the primary interface to the whole application. The user will spend most of the time here. Other user interfaces must be accessible from the Geometry Designer UI. The primary purpose of the Geometry Designer UI is to provide the user with the ability to construct a geometry to feed into the FEM solver backend.

### Capabilities (high level)
* Can build a custom geometry and export to backend
* Can open a dedicated UI for slicing a cross section of a 2.5D CAD layout (e.g. kicad layout or gerber)
* Can show basic rough estimates of transmission line parameters.

### User Requirements
* User must be able to export the created geometry to the FEM solver backend
* User must be able to use the Geometry Designer UI to design a geometry manually by specifying layers, elements, sizes, etc.
* User must be able to select from common types of planar transmission line geometries as presets
* User must be able to create a custom planar transmission line geometry 
* User must be able to see a rough estimate of the characteristic impedence of the chosen port
* User must be able to see a rough estimate of the effective relative permittivity of the chosen port
* User must be able to select which ports to calculate the transmission line parameters on.

### planar geometry creation
* Layers are vertically stacking, and are representative of layers in a PCB
* Layers may contain elements, representative of the physical things which exist on that layer.
* Elements may substrates, such as FR4, conductors, such as copper, empty space, such as air or vacuum. Vias also exist as an element.
* All layers shall conform to the same total outer dimension. In other words, if the bottom layer is 100mm wide, and the top layer only has a narrow conducter of 20mm wide, the rest of the space should be filled with a spacer of either air or vacuum such that the top layer has the same outer dimension as the largest outer dimension.
* Vias are able to be added in a layer, and span the height of a layer
* The width of a via can be specified
* The width and height of each element can be specified.
* The FEM solving parameters (such as conductivity, relative permittivity, etc) can be specified for each individual element
* Sizing parameters between two or more elements can be "linked" so that they have the same value. This allows adjusting multiple elements simultaneously and ensures that tracks are the same value if this is desired.
* Conductors can be specified as either ground or signal 1, signal 2, signal 3, etc.
* Ports can be specified as a collection of two conductors, one specified as reference and the other specified as the input.

## Solver backend
* The solver can accept the export format from the Geometry Designer UI
* The solver can be controlled from either the Geometry Designer UI or a dedicated GUI accessible from the Geometry Designer UI
* The solver uses FEM methods
* The solver meshes the given geometry
* The solver uses the mesh to solve maxwells equations numerically
* The solver uses the field solution to then solve for RLGC parameters of the transmission line
* The solver uses the exported geometry to decide what is a conductor and what is not
* The solver uses the exported geometry to decide what is the port of interest
* Ports may be defined as a signal source between two conductor. e.g. in microstrip it might be the single microstrip line and the ground plane. In differential pair the port could be *either* from one signal conductor to the other, or from one signal conductor to ground, or from both signal conductors to ground.
* The solver uses python or C and can be tested from the browser. Copilot should be able to test.
