"""
GitHub Copilot instructions for this workspace
"""

## Virtual Electrical Designer & Simulator - Development Guide

### Project Overview
This is a comprehensive desktop application for designing and simulating electrical circuits and power systems using Python with PySide6 for the UI and NumPy/SciPy for numerical computations.

### Directory Structure
- `src/frontend/`: PySide6 UI components
  - `ui/`: Main window, dialogs, menu bar, toolbar
  - `panels/`: Reusable panel components (library, inspector, console, waveform, etc.)
- `src/backend/`: Core simulation and analysis engines
  - `circuit/`: Circuit model, project management, component library
  - `simulation/`: DC/AC/transient solvers
  - `power_systems/`: Three-phase and fault analysis
  - `design_wizards/`: Engineering calculation tools
  - `reporting/`: Report generation and export
  - `ai_helper/`: Intelligent circuit assistance
  - `scripting/`: Python script runtime

### Key Technologies
- **PySide6**: Qt-based GUI framework
- **pyqtgraph**: Fast plotting for waveforms
- **NumPy/SciPy**: Numerical computations
- **SymPy**: Symbolic mathematics
- **NetworkX**: Circuit topology analysis

### Running the Application
```bash
pip install -r requirements.txt
python -m src.frontend.main
```

### Development Guidelines
1. **Frontend**: All UI components inherit from PySide6.QtWidgets
2. **Backend**: Modular design with clear separation of concerns
3. **Testing**: Use pytest for unit tests in `tests/` directory
4. **Documentation**: Add docstrings to all public methods
5. **File Formats**: `.vedproj` (project), `.vedcir` (circuit), `.vedlib` (library)
