"""
Circuit Model - nodes, components, connections, and multi-circuit support
"""
from typing import Dict, List, Tuple, Optional
from enum import Enum


class ComponentType(Enum):
    """Enumeration of component types"""
    RESISTOR = "resistor"
    CAPACITOR = "capacitor"
    INDUCTOR = "inductor"
    VOLTAGE_SOURCE = "voltage_source"
    CURRENT_SOURCE = "current_source"
    DIODE = "diode"
    TRANSISTOR = "transistor"
    TRANSFORMER = "transformer"
    MOTOR = "motor"
    GENERATOR = "generator"


class Node:
    """Represents a node in the circuit"""
    
    def __init__(self, node_id: str, name: str = ""):
        self.id = node_id
        self.name = name or f"Node_{node_id}"
        self.voltage = 0.0
        self.connected_components: List[str] = []
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "voltage": self.voltage,
        }


class Component:
    """Base class for circuit components"""
    
    def __init__(self, comp_id: str, comp_type: ComponentType, name: str = ""):
        self.id = comp_id
        self.type = comp_type
        self.name = name or f"{comp_type.value}_{comp_id}"
        self.nodes: List[str] = []  # Connected node IDs
        self.parameters: Dict[str, float] = {}
        self.x = 0.0
        self.y = 0.0
        
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "nodes": self.nodes,
            "parameters": self.parameters,
            "x": self.x,
            "y": self.y,
        }


class Circuit:
    """Represents a single circuit"""
    
    def __init__(self, circuit_id: str, name: str = ""):
        self.id = circuit_id
        self.name = name or f"Circuit_{circuit_id}"
        self.nodes: Dict[str, Node] = {}
        self.components: Dict[str, Component] = {}
        self.connections: List[Tuple[str, str]] = []  # (from_comp, to_comp)
        
    def add_node(self, node_id: str, name: str = "") -> Node:
        """Add a node to the circuit"""
        node = Node(node_id, name)
        self.nodes[node_id] = node
        return node
        
    def add_component(self, comp_id: str, comp_type: ComponentType, name: str = "") -> Component:
        """Add a component to the circuit"""
        component = Component(comp_id, comp_type, name)
        self.components[comp_id] = component
        return component
        
    def connect(self, node_id: str, comp_id: str):
        """Connect a component to a node"""
        if node_id in self.nodes and comp_id in self.components:
            self.components[comp_id].nodes.append(node_id)
            self.nodes[node_id].connected_components.append(comp_id)
            
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "components": {cid: comp.to_dict() for cid, comp in self.components.items()},
            "connections": self.connections,
        }


class CircuitModel:
    """Manages multiple circuits and their connections"""
    
    def __init__(self):
        self.circuits: Dict[str, Circuit] = {}
        self.circuit_count = 0
        
    def create_circuit(self, name: str = "") -> Circuit:
        """Create a new circuit"""
        circuit_id = f"circuit_{self.circuit_count}"
        circuit = Circuit(circuit_id, name)
        self.circuits[circuit_id] = circuit
        self.circuit_count += 1
        return circuit
        
    def get_circuit(self, circuit_id: str) -> Optional[Circuit]:
        """Get circuit by ID"""
        return self.circuits.get(circuit_id)
        
    def remove_circuit(self, circuit_id: str) -> bool:
        """Remove a circuit"""
        if circuit_id in self.circuits:
            del self.circuits[circuit_id]
            return True
        return False
        
    def to_dict(self):
        return {
            "circuits": {cid: circuit.to_dict() for cid, circuit in self.circuits.items()},
        }
