from setuptools import setup, find_packages

setup(
    name="virtual-electrical-designer",
    version="0.1.0",
    description="A comprehensive desktop application for designing and simulating electrical circuits",
    author="Surya B",
    author_email="myselfsuryaaz@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.6.1",
        "pyqtgraph>=0.13.7",
        "numpy>=1.24.3",
        "scipy>=1.11.1",
        "matplotlib>=3.8.0",
        "pandas>=2.1.0",
        "networkx>=3.2",
        "sympy>=1.12",
    ],
    entry_points={
        "console_scripts": [
            "ved=frontend.main:main",
        ],
    },
)

