from setuptools import setup, find_packages

setup(
    name="2d-em-solver",
    version="0.1.0",
    description="A 2D electromagnetic field solver for transmission line analysis",
    author="Nathan Greg Kidd",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "2d-em-solver=em_solver.cli:main",
        ],
    },
)