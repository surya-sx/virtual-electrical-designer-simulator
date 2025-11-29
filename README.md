# Virtual Electrical Designer & Simulator

A comprehensive desktop application for designing, simulating, and analyzing electrical circuits and power systems.

## Features

- **Circuit Design**: Intuitive drag-and-drop interface for building electrical circuits
- **Multi-type Simulation**: DC, AC, transient, parametric sweep, and Monte Carlo analysis
- **Power Systems Analysis**: Three-phase load flow, fault analysis, and protection curves
- **Design Wizards**: Transformer design, cable sizing, power factor correction, and battery sizing
- **Component Library**: Built-in and customizable component libraries
- **Reports & Export**: Generate comprehensive reports and export in PDF, HTML, CSV, PNG, and SVG formats
- **AI-powered Assistant**: Circuit error checking, fix suggestions, and component explanations
- **Script Editor**: Python scripting interface for advanced automation

## Project Structure

```
virtual-electrical-designer/
├── src/
│   ├── frontend/              # PySide6 UI components
│   │   ├── ui/               # Main window and dialogs
│   │   └── panels/           # Panel components (library, inspector, console, etc.)
│   └── backend/              # Core simulation and analysis engines
│       ├── circuit/          # Circuit model and management
│       ├── simulation/       # DC/AC/transient solvers
│       ├── power_systems/    # Three-phase and fault analysis
│       ├── design_wizards/   # Design calculation tools
│       ├── reporting/        # Report generation
│       ├── ai_helper/        # AI-assisted features
│       └── scripting/        # Python script runtime
├── data/
│   ├── projects/             # User project files (.vedproj, .vedcir)
│   ├── libraries/            # Component libraries (.vedlib)
│   └── exports/              # Generated exports (PDF, HTML, CSV, etc.)
├── docs/                      # Documentation
├── tests/                     # Unit and integration tests
└── requirements.txt           # Python dependencies
```

## Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python -m src.frontend.main
```

## Current Status

✅ **All Features Operational**
- Main application running and fully functional
- All 7 menus (File, Edit, View, Simulation, Tools, Window, Help) connected and working
- 6 Engineering tools available (Transformer Designer, Cable Sizing, Fault Calculator, PF Correction, Battery Tool, Library Manager)
- Script Editor fully functional
- All toolbar buttons and keyboard shortcuts working

See `FIX_SUMMARY.md` for latest fixes and `VALIDATION_REPORT.md` for detailed verification.

## Technology Stack

- **Frontend**: Python, PySide6, pyqtgraph
- **Backend**: Python with NumPy, SciPy, SymPy, NetworkX
- **Data Formats**:
  - Projects: `.vedproj`
  - Circuits: `.vedcir`
  - Component Libraries: `.vedlib`
  - Exports: `.csv`, `.pdf`, `.html`, `.png`, `.svg`

## Development

### Backend Modules

- **ProjectManager**: Project lifecycle management
- **CircuitModel**: Node/component graph representation
- **SimulationEngine**: DC/AC/transient solvers
- **PowerSystemEngine**: Three-phase and fault analysis
- **DesignWizardsEngine**: Engineering calculation tools
- **ReportGenerator**: Report and export generation
- **AIHelper**: Intelligent circuit assistance
- **ScriptRuntime**: Custom Python script execution

### Frontend Components

- **MenuBar**: File, Edit, View, Simulation, Tools, Window, Help menus
- **MainToolbar**: Quick access to common operations
- **ComponentLibraryPanel**: Searchable component catalog
- **CircuitCanvas**: Interactive circuit editor with grid and pan/zoom
- **InspectorPanel**: Component, circuit, and simulation properties
- **ConsolePanel**: Log viewer with filtering
- **WaveformPanel**: Signal visualization with cursors
- **ReportsPanel**: Summary, BOM, and results
- **ScriptEditorPanel**: Python code editor and execution

