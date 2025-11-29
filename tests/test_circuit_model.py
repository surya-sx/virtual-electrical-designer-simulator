"""Test suite for circuit model"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from backend.circuit.circuit_model import Circuit, CircuitModel, ComponentType


class TestCircuitModel:
    """Test circuit model functionality"""
    
    def test_create_node(self):
        """Test node creation"""
        circuit = Circuit("test_circuit", "Test Circuit")
        node = circuit.add_node("n1", "Node 1")
        
        assert node.id == "n1"
        assert node.name == "Node 1"
        assert "n1" in circuit.nodes
        
    def test_add_component(self):
        """Test component addition"""
        circuit = Circuit("test_circuit")
        comp = circuit.add_component("r1", ComponentType.RESISTOR, "R1")
        
        assert comp.id == "r1"
        assert comp.type == ComponentType.RESISTOR
        assert "r1" in circuit.components
        
    def test_connect_component_to_node(self):
        """Test connecting component to node"""
        circuit = Circuit("test_circuit")
        node = circuit.add_node("n1")
        comp = circuit.add_component("r1", ComponentType.RESISTOR)
        
        circuit.connect("n1", "r1")
        
        assert "n1" in comp.nodes
        assert "r1" in node.connected_components
        
    def test_multi_circuit_model(self):
        """Test multi-circuit model"""
        model = CircuitModel()
        
        circuit1 = model.create_circuit("Circuit 1")
        circuit2 = model.create_circuit("Circuit 2")
        
        assert len(model.circuits) == 2
        assert model.get_circuit("circuit_0") == circuit1
        assert model.get_circuit("circuit_1") == circuit2
        
    def test_remove_circuit(self):
        """Test circuit removal"""
        model = CircuitModel()
        circuit = model.create_circuit("Test")
        
        assert model.remove_circuit("circuit_0")
        assert len(model.circuits) == 0
        assert model.remove_circuit("circuit_0") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
