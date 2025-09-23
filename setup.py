from setuptools import setup, find_packages

setup(
    name="kicad-2d-em-solver",
    version="0.1.0",
    description="A 2D EM solver able to slice KiCAD and other layout types",
    author="2D_EM_solver",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "shapely>=2.0.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "kicad-slicer=kicad_slicer.cli:main",
        ],
    },
    python_requires=">=3.8",
)