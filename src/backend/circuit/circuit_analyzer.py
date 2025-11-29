"""
Circuit Analysis Utilities - topology analysis, node numbering, connectivity
"""
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict, deque


class CircuitAnalyzer:
    """Analyzes circuit topology and properties"""
    
    def __init__(self):
        self.node_mapping: Dict[str, int] = {}
        self.adjacency_list: Dict[str, List[str]] = defaultdict(list)
    
    def analyze_circuit(self, circuit_data: Dict) -> Dict:
        """
        Perform comprehensive circuit analysis
        
        Args:
            circuit_data: Dict with components, nodes, wires
        
        Returns:
            Dict with analysis results
        """
        components = circuit_data.get("components", {})
        wires = circuit_data.get("wires", [])
        
        # Build graph
        self._build_adjacency_list(components, wires)
        
        return {
            "node_count": self._count_nodes(components),
            "component_count": len(components),
            "wire_count": len(wires),
            "connectivity": self._analyze_connectivity(components),
            "node_mapping": self._number_nodes(components),
            "meshes": self._find_meshes(components, wires),
            "component_types": self._count_component_types(components),
            "is_planar": self._is_planar_circuit(components, wires),
        }
    
    def _build_adjacency_list(self, components: Dict, wires: List):
        """Build adjacency list from circuit"""
        self.adjacency_list.clear()
        
        for comp_id in components:
            self.adjacency_list[comp_id] = []
        
        for wire in wires:
            if isinstance(wire, dict):
                from_id = wire.get("from")
                to_id = wire.get("to")
                
                if from_id in self.adjacency_list and to_id in self.adjacency_list:
                    if to_id not in self.adjacency_list[from_id]:
                        self.adjacency_list[from_id].append(to_id)
                    if from_id not in self.adjacency_list[to_id]:
                        self.adjacency_list[to_id].append(from_id)
    
    def _count_nodes(self, components: Dict) -> int:
        """Count electrical nodes in circuit"""
        nodes_set: Set[Tuple[int, int]] = set()
        
        for comp in components.values():
            if isinstance(comp, dict):
                x = comp.get("x", 0)
                y = comp.get("y", 0)
                nodes_set.add((round(x / 20) * 20, round(y / 20) * 20))
        
        return len(nodes_set)
    
    def _number_nodes(self, components: Dict) -> Dict[str, int]:
        """Assign node numbers to components"""
        self.node_mapping.clear()
        node_counter = 0
        position_to_node: Dict[Tuple[float, float], int] = {}
        
        # Group components by position (assuming connection points at corners)
        components_by_position: Dict[Tuple[int, int], List[str]] = defaultdict(list)
        
        for comp_id, comp in components.items():
            if isinstance(comp, dict):
                x = comp.get("x", 0)
                y = comp.get("y", 0)
                pos = (round(x / 20) * 20, round(y / 20) * 20)
                components_by_position[pos].append(comp_id)
        
        # Assign node numbers
        for comps_at_pos in components_by_position.values():
            for comp_id in comps_at_pos:
                self.node_mapping[comp_id] = node_counter
            node_counter += 1
        
        return self.node_mapping
    
    def _analyze_connectivity(self, components: Dict) -> Dict:
        """Analyze circuit connectivity"""
        if not components:
            return {"connected_components": 0, "isolated_components": 0}
        
        visited = set()
        connected_groups = 0
        
        for comp_id in components:
            if comp_id not in visited:
                # BFS to find connected component
                queue = deque([comp_id])
                visited.add(comp_id)
                
                while queue:
                    current = queue.popleft()
                    for neighbor in self.adjacency_list.get(current, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                connected_groups += 1
        
        isolated = len([c for c in components if not self.adjacency_list.get(c, [])])
        
        return {
            "connected_components": len(visited),
            "isolated_components": isolated,
            "separate_groups": connected_groups,
        }
    
    def _find_meshes(self, components: Dict, wires: List) -> List[List[str]]:
        """Find elementary meshes in circuit (planar circuits)"""
        meshes: List[List[str]] = []
        
        # Simple mesh detection for planar circuits
        # In a planar circuit, mesh = face in planar graph
        # Using a simplified approach: find cycles
        
        visited_edges = set()
        
        for start_comp in components:
            for neighbor in self.adjacency_list.get(start_comp, []):
                edge = tuple(sorted([start_comp, neighbor]))
                if edge in visited_edges:
                    continue
                
                visited_edges.add(edge)
                
                # Find cycle containing this edge (simplified)
                cycle = self._find_cycle(start_comp, neighbor, components)
                if cycle and len(cycle) > 2:
                    meshes.append(cycle)
        
        return meshes
    
    def _find_cycle(self, start: str, next_node: str, components: Dict, path: Optional[List[str]] = None) -> Optional[List[str]]:
        """Find a cycle in the graph"""
        if path is None:
            path = [start]
        
        if next_node in path and len(path) > 2:
            # Cycle found
            cycle_start = path.index(next_node)
            return path[cycle_start:] + [next_node]
        
        if next_node in path:
            return None
        
        new_path = path + [next_node]
        
        for neighbor in self.adjacency_list.get(next_node, []):
            if neighbor == start and len(new_path) > 2:
                return new_path
            
            if neighbor not in new_path:
                cycle = self._find_cycle(start, neighbor, components, new_path)
                if cycle:
                    return cycle
        
        return None
    
    def _count_component_types(self, components: Dict) -> Dict[str, int]:
        """Count components by type"""
        type_count = defaultdict(int)
        
        for comp in components.values():
            if isinstance(comp, dict):
                comp_type = comp.get("type", "unknown").lower()
                type_count[comp_type] += 1
        
        return dict(type_count)
    
    def _is_planar_circuit(self, components: Dict, wires: List) -> bool:
        """Check if circuit is planar (simplified)"""
        # Euler's formula for planar graphs: V - E + F = 2
        # For now, assume most circuits are planar if they can be drawn without crossings
        
        V = len(components)
        E = len(wires)
        
        if V <= 2:
            return True
        
        # Simplified check: max edges in planar graph is 3V - 6
        max_edges = 3 * V - 6
        
        return E <= max_edges
    
    def get_component_neighbors(self, component_id: str) -> List[str]:
        """Get neighbors of a component"""
        return self.adjacency_list.get(component_id, [])
    
    def get_connectivity_matrix(self, components: Dict) -> List[List[int]]:
        """Get connectivity/adjacency matrix"""
        comp_ids = list(components.keys())
        n = len(comp_ids)
        
        matrix = [[0] * n for _ in range(n)]
        
        for i, comp_id_1 in enumerate(comp_ids):
            for j, comp_id_2 in enumerate(comp_ids):
                if comp_id_2 in self.adjacency_list.get(comp_id_1, []):
                    matrix[i][j] = 1
        
        return matrix
