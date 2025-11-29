"""Integration tests for UI and backend interaction"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import numpy as np
from backend.circuit.circuit_model import CircuitModel, ComponentType
from backend.simulation.simulation_engine import SimulationEngine
from backend.circuit.project_manager import ProjectManager
from backend.circuit.component_library import ComponentLibraryManager


class TestCircuitSimulationIntegration:
    """Test circuit model and simulation integration"""
    
    def test_create_and_simulate_circuit(self):
        """Test creating a circuit and running simulation"""
        model = CircuitModel()
        engine = SimulationEngine()
        
        # Create circuit
        circuit = model.create_circuit("Test Circuit")
        
        # Add nodes
        node_1 = circuit.add_node("n1", "Node 1")
        node_2 = circuit.add_node("n2", "Node 2")
        node_3 = circuit.add_node("n3", "GND")
        
        # Add components
        vs = circuit.add_component("v1", ComponentType.VOLTAGE_SOURCE, "V1")
        r = circuit.add_component("r1", ComponentType.RESISTOR, "R1")
        
        # Set parameters
        vs.parameters = {"voltage": 5.0}
        r.parameters = {"resistance": 1000.0}
        
        # Connect components
        circuit.connect("n1", "v1")
        circuit.connect("n3", "v1")
        circuit.connect("n1", "r1")
        circuit.connect("n2", "r1")
        
        # Run simulation
        engine.setup_dc_analysis()
        result = engine.run()
        
        assert result.status == "success"
        assert len(result.time_points) > 0
    
    def test_project_save_and_load(self):
        """Test project save and load functionality"""
        manager = ProjectManager()
        
        # Create and save project
        project = manager.create_project("Test Project")
        assert project is not None
        assert manager.save_project(project)
        
        # Load project
        loaded = manager.load_project(project.path)
        assert loaded.name == "Test Project"
        assert loaded.path == project.path
    
    def test_component_library_access(self):
        """Test component library access"""
        lib_manager = ComponentLibraryManager()
        
        # Get component
        resistor = lib_manager.get_component("Resistor")
        assert resistor is not None
        assert resistor.name == "Resistor"
        assert "resistance" in resistor.parameters
        
        # Get all categories
        categories = lib_manager.get_all_categories()
        assert "Passive" in categories
        assert "Sources" in categories
        
        # Get components by category
        passive = lib_manager.list_components_by_category("Passive")
        assert len(passive) > 0


class TestSimulationResultsProcessing:
    """Test simulation results processing"""
    
    def test_dc_analysis_results(self):
        """Test DC analysis produces valid results"""
        engine = SimulationEngine()
        engine.setup_dc_analysis()
        result = engine.run()
        
        assert result.status == "success"
        assert len(result.time_points) == 1  # DC has single time point
        assert isinstance(result.time_points, np.ndarray)
        assert isinstance(result.node_voltages, dict)
    
    def test_transient_analysis_results(self):
        """Test transient analysis produces time-domain results"""
        engine = SimulationEngine()
        engine.setup_transient_analysis(duration=0.1, time_step=0.001)
        result = engine.run()
        
        assert result.status == "success"
        assert len(result.time_points) > 1
        assert result.time_points[-1] >= 0.1


class TestCircuitCanvasModel:
    """Test circuit canvas data model"""
    
    def test_add_components_to_canvas(self):
        """Test adding components to canvas model"""
        from src.frontend.panels.circuit_canvas import CircuitCanvas
        
        canvas = CircuitCanvas()
        
        # Add components
        comp1 = canvas.add_component("Resistor", "R1", 100, 100)
        comp2 = canvas.add_component("Capacitor", "C1", 200, 100)
        
        assert comp1 in canvas.components
        assert comp2 in canvas.components
        assert len(canvas.components) == 2
    
    def test_add_wires_to_canvas(self):
        """Test adding wires (connections) to canvas"""
        from src.frontend.panels.circuit_canvas import CircuitCanvas
        
        canvas = CircuitCanvas()
        
        # Add components to create nodes
        canvas.add_component("Resistor", "R1", 100, 100)
        
        # Get nodes
        node_ids = list(canvas.nodes.keys())
        assert len(node_ids) >= 2
        
        # Add wire
        wire_id = canvas.add_wire(node_ids[0], node_ids[1])
        assert wire_id is not None
        assert wire_id in canvas.wires
    
    def test_component_selection(self):
        """Test component selection on canvas"""
        from src.frontend.panels.circuit_canvas import CircuitCanvas
        
        canvas = CircuitCanvas()
        comp_id = canvas.add_component("Resistor", "R1", 100, 100)
        
        canvas.select_component(comp_id)
        assert canvas.selected_component == comp_id
        assert canvas.components[comp_id].selected
    
    def test_component_movement(self):
        """Test moving components on canvas"""
        from src.frontend.panels.circuit_canvas import CircuitCanvas
        
        canvas = CircuitCanvas()
        comp_id = canvas.add_component("Resistor", "R1", 100, 100)
        original_pos = (canvas.components[comp_id].x, canvas.components[comp_id].y)
        
        canvas.move_component(comp_id, 50, 50)
        new_pos = (canvas.components[comp_id].x, canvas.components[comp_id].y)
        
        assert new_pos[0] == original_pos[0] + 50
        assert new_pos[1] == original_pos[1] + 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
