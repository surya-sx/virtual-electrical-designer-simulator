"""
Circuit Validator - checks circuit topology, connectivity, and validity
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    level: ValidationLevel
    component_id: Optional[str]
    message: str
    suggestion: Optional[str] = None


class CircuitValidator:
    """Validates circuit topology and connections"""
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
    
    def validate_circuit(self, circuit_data: Dict) -> Tuple[bool, List[ValidationIssue]]:
        """
        Validate entire circuit
        
        Args:
            circuit_data: Dict with components, nodes, wires
        
        Returns:
            Tuple of (is_valid, issues_list)
        """
        self.issues.clear()
        
        components = circuit_data.get("components", {})
        nodes = circuit_data.get("nodes", [])
        wires = circuit_data.get("wires", [])
        
        # Check basic structure
        self._check_empty_circuit(components, nodes, wires)
        
        # Check components
        self._check_isolated_components(components, wires)
        self._check_component_connectivity(components, wires)
        
        # Check circuit topology
        self._check_ground_reference(components, nodes)
        self._check_sources(components)
        self._check_loops(components, wires)
        
        # Determine if valid (errors = invalid, warnings/info = valid but with issues)
        is_valid = not any(issue.level == ValidationLevel.ERROR for issue in self.issues)
        
        return is_valid, self.issues
    
    def _check_empty_circuit(self, components: Dict, nodes: List, wires: List):
        """Check if circuit has components"""
        if not components:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                component_id=None,
                message="Circuit is empty",
                suggestion="Add components from the library to build your circuit"
            ))
    
    def _check_isolated_components(self, components: Dict, wires: List):
        """Check for isolated components with no connections"""
        connected_comps = set()
        
        for wire in wires:
            if isinstance(wire, dict):
                connected_comps.add(wire.get("from"))
                connected_comps.add(wire.get("to"))
        
        for comp_id, comp in components.items():
            if comp_id not in connected_comps:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    component_id=comp_id,
                    message=f"Component {comp.get('name', comp_id)} is not connected",
                    suggestion="Connect this component to other components using wires"
                ))
    
    def _check_component_connectivity(self, components: Dict, wires: List):
        """Check if component connections are valid"""
        for wire in wires:
            if not isinstance(wire, dict):
                continue
            
            from_id = wire.get("from")
            to_id = wire.get("to")
            
            if from_id and from_id not in components:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    component_id=None,
                    message=f"Wire references non-existent component: {from_id}",
                    suggestion="Remove this wire and reconnect to valid components"
                ))
            
            if to_id and to_id not in components:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    component_id=None,
                    message=f"Wire references non-existent component: {to_id}",
                    suggestion="Remove this wire and reconnect to valid components"
                ))
    
    def _check_ground_reference(self, components: Dict, nodes: List):
        """Check if circuit has a ground reference"""
        has_ground = any(
            comp.get("type", "").lower() == "ground" 
            for comp in components.values() if isinstance(comp, dict)
        )
        
        if not has_ground and components:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                component_id=None,
                message="Circuit has no ground reference",
                suggestion="Add a ground component to establish reference potential"
            ))
    
    def _check_sources(self, components: Dict):
        """Check if circuit has voltage or current sources"""
        has_sources = any(
            comp.get("type", "").lower() in ["voltage_source", "current_source", "voltage source", "current source"]
            for comp in components.values() if isinstance(comp, dict)
        )
        
        if not has_sources and components:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                component_id=None,
                message="Circuit has no voltage or current sources",
                suggestion="Add a voltage or current source to analyze the circuit"
            ))
    
    def _check_loops(self, components: Dict, wires: List):
        """Check for floating loops and incomplete paths"""
        # Build adjacency list
        adjacency: Dict[str, List[str]] = {}
        
        for comp_id in components:
            adjacency[comp_id] = []
        
        for wire in wires:
            if not isinstance(wire, dict):
                continue
            
            from_id = wire.get("from")
            to_id = wire.get("to")
            
            if from_id in adjacency and to_id in adjacency:
                if to_id not in adjacency[from_id]:
                    adjacency[from_id].append(to_id)
                if from_id not in adjacency[to_id]:
                    adjacency[to_id].append(from_id)
        
        # Check connectivity (simple DFS)
        if adjacency:
            visited = set()
            start_node = next(iter(adjacency.keys()))
            self._dfs(start_node, adjacency, visited)
            
            unvisited = set(adjacency.keys()) - visited
            if unvisited:
                for comp_id in unvisited:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        component_id=comp_id,
                        message=f"Component {components.get(comp_id, {}).get('name', comp_id)} is disconnected from main circuit",
                        suggestion="Connect this component to the rest of the circuit"
                    ))
    
    def _dfs(self, node: str, adjacency: Dict[str, List[str]], visited: set):
        """Depth-first search for connectivity check"""
        visited.add(node)
        for neighbor in adjacency.get(node, []):
            if neighbor not in visited:
                self._dfs(neighbor, adjacency, visited)
    
    def get_issues_by_level(self, level: ValidationLevel) -> List[ValidationIssue]:
        """Get issues filtered by severity level"""
        return [issue for issue in self.issues if issue.level == level]
