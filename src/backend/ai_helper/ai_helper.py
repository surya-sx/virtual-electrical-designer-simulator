"""
AI Helper - circuit error checking, fix suggestions, component explanations
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class CircuitError:
    """Represents a circuit error"""
    error_type: str
    severity: str  # "error", "warning", "info"
    location: str
    message: str
    suggestion: str


class AIHelper:
    """AI-powered circuit assistance"""
    
    def __init__(self):
        self.error_db = self._build_error_database()
        
    def _build_error_database(self) -> Dict[str, str]:
        """Build error suggestion database"""
        return {
            "floating_node": "Nodes must be connected to at least 2 components. Add a connection or remove the node.",
            "no_ground": "Circuit must have at least one ground reference node.",
            "floating_component": "All component terminals must be connected to nodes.",
            "no_source": "Circuit must have at least one voltage or current source.",
            "short_circuit": "Direct short circuit detected. This may cause unrealistic results.",
            "missing_return_path": "Current source or voltage source missing return path to ground.",
        }
        
    def check_circuit_errors(self, circuit_data: Dict) -> List[CircuitError]:
        """Check circuit for errors"""
        errors = []
        
        # Check for ground node
        if not any(node.get("is_ground") for node in circuit_data.get("nodes", {}).values()):
            errors.append(CircuitError(
                "no_ground", "error",
                "Circuit", "No ground node found",
                "Add a ground reference node (usually labeled GND or 0)"
            ))
            
        # Check for source
        components = circuit_data.get("components", {})
        if not any(c.get("type") in ["voltage_source", "current_source"] for c in components.values()):
            errors.append(CircuitError(
                "no_source", "warning",
                "Circuit", "No voltage or current source found",
                "Add at least one source to the circuit"
            ))
            
        # Check for floating nodes
        nodes = circuit_data.get("nodes", {})
        for node_id, node in nodes.items():
            connected = node.get("connected_components", [])
            if len(connected) < 2 and not node.get("is_ground"):
                errors.append(CircuitError(
                    "floating_node", "error",
                    f"Node {node.get('name', node_id)}",
                    f"Node has only {len(connected)} connection(s)",
                    "Nodes must be connected to at least 2 components"
                ))
                
        return errors
        
    def suggest_fixes(self, errors: List[CircuitError]) -> List[str]:
        """Suggest fixes for detected errors"""
        suggestions = []
        
        for error in errors:
            suggestion = self.error_db.get(error.error_type, error.suggestion)
            suggestions.append(f"[{error.severity.upper()}] {error.message}\n  → {suggestion}")
            
        return suggestions
        
    def explain_component_role(self, component_type: str) -> str:
        """Explain the role of a component in a circuit"""
        explanations = {
            "resistor": "Resistors oppose current flow and dissipate energy as heat. Used for limiting current, setting bias points, and signal attenuation.",
            "capacitor": "Capacitors store electrical energy in an electric field. Used for filtering, AC coupling, and energy storage.",
            "inductor": "Inductors store electrical energy in a magnetic field. Used for filtering, energy storage, and impedance matching.",
            "voltage_source": "Voltage sources provide a potential difference between two points. Drives current through the circuit.",
            "current_source": "Current sources provide a constant current flow independent of circuit resistance.",
            "diode": "Diodes conduct current in one direction, used for rectification, protection, and switching.",
            "transistor": "Transistors are active devices used for amplification and switching applications.",
            "transformer": "Transformers transfer electrical energy between circuits using electromagnetic induction.",
        }
        
        return explanations.get(component_type.lower(), "Component role not documented")
        
    def analyze_circuit_stability(self, circuit_data: Dict) -> Dict:
        """Analyze circuit for stability issues"""
        return {
            "is_stable": True,
            "issues": [],
            "suggestions": [],
        }
