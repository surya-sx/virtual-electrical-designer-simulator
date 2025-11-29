"""
Circuit canvas - main drawing area for circuits
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import copy

from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu
from PySide6.QtCore import Qt, QPoint, QSize, QRect, Signal, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QFont, QPolygon, QAction
import math

from frontend.ui.properties_dialog import PropertiesDialog


class CanvasMode(Enum):
    """Canvas operation mode"""
    SELECT = "select"
    PLACE_COMPONENT = "place"
    DRAW_WIRE = "wire"
    MARQUEE = "marquee"
    PAN = "pan"


@dataclass
class Node:
    """Canvas node (connection point)"""
    x: float
    y: float
    node_id: str
    connections: List[str] = None
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []
    
    def distance_to(self, x: float, y: float) -> float:
        """Calculate distance to point"""
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)


@dataclass
class Wire:
    """Canvas wire (connection)"""
    from_node: str
    to_node: str
    wire_id: str


@dataclass
class CanvasComponent:
    """Component on canvas"""
    x: float
    y: float
    comp_id: str
    comp_type: str
    name: str
    width: float = 60
    height: float = 40
    selected: bool = False
    params: Dict = None
    properties: Dict = None  # Component properties from library
    rotation: float = 0.0  # Rotation in degrees (0, 90, 180, 270)
    group_id: Optional[str] = None  # Group ID if part of group
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}
        if self.properties is None:
            self.properties = {}
        # Normalize rotation to 0-360
        self.rotation = self.rotation % 360
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside component (bounding box)"""
        return (self.x - self.width/2 <= x <= self.x + self.width/2 and
                self.y - self.height/2 <= y <= self.y + self.height/2)
    
    def get_ports(self) -> List[Tuple[float, float]]:
        """Get port positions based on component type"""
        left = self.x - self.width/2
        right = self.x + self.width/2
        
        # Ground/reference has only 1 port at the top
        if "ground" in self.comp_type.lower():
            return [(self.x, self.y - 15)]  # Single top port for ground connection
        
        # Return 2 ports (left and right) for 2-terminal components
        return [
            (left, self.y),      # Left
            (right, self.y),     # Right
        ]


class CircuitCanvas(QWidget):
    """Main canvas for drawing and editing circuits"""
    
    # Signals
    component_selected = Signal(str)  # component_id
    component_placed = Signal(str, float, float)  # comp_id, x, y
    circuit_changed = Signal()
    undo_redo_changed = Signal(bool, bool)  # can_undo, can_redo - for toolbar updates
    clipboard_changed = Signal(bool)  # has_content
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f5f5f5;")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAcceptDrops(True)

        # Canvas state
        self.grid_size = 20
        self.show_grid = True
        self.snap_to_grid = True  # Snap to grid when placing/moving
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.wire_width = 2  # Width of drawn wires

        # Circuit elements
        self.components: Dict[str, CanvasComponent] = {}
        self.nodes: Dict[str, Node] = {}
        self.wires: Dict[str, Wire] = {}
        self.groups: Dict[str, List[str]] = {}  # group_id -> [comp_ids]
        self.node_counter = 0
        self.wire_counter = 0
        self.group_counter = 0

        # Selection and interaction
        self.mode = CanvasMode.SELECT  # Default mode but wire logic is always active
        self.selected_component: Optional[str] = None
        self.selected_components: List[str] = []  # Multi-select
        self.dragging = False
        self.drag_start = QPoint()
        self.preview_component: Optional[CanvasComponent] = None

        # Wire drawing mode
        self.wire_mode_start_node: Optional[str] = None
        self.wire_preview: Optional[tuple] = None  # ((x1, y1), (x2, y2)) for preview line
        
        # Marquee selection
        self.marquee_start: Optional[QPoint] = None
        self.marquee_rect: Optional[QRect] = None
        self.marquee_mode = False
        
        # Node to component mapping for better tracking
        self.node_to_component: Dict[str, str] = {}  # node_id -> comp_id
        
        # Undo/Redo system
        self.undo_stack: List[Dict] = []  # History of states
        self.redo_stack: List[Dict] = []
        self.max_undo_levels = 50
        
        # Clipboard for cut/copy/paste
        
        # Auto-fix existing ground components on load
        self._auto_fix_ground_components()
        self.clipboard: Dict = {"components": [], "nodes": [], "wires": []}

    def dragEnterEvent(self, event):
        """Accept drag enter events"""
        if event.mimeData().hasFormat("component/type") or event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """Accept drag move events"""
        event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event - place component on canvas"""
        mime = event.mimeData()
        
        # Extract component info from mime data
        comp_type = None
        comp_name = None
        
        if mime.hasFormat("component/type"):
            comp_type = mime.data("component/type").data().decode('utf-8')
            comp_name = mime.data("component/name").data().decode('utf-8')
        elif mime.hasText():
            text = mime.text()
            if "|" in text:
                comp_type, comp_name = text.split("|", 1)
        
        if comp_type and comp_name:
            # Get drop position
            pos = event.position().toPoint()
            x = float(pos.x())
            y = float(pos.y())
            
            # Snap to grid if enabled
            if self.snap_to_grid:
                x = round(x / self.grid_size) * self.grid_size
                y = round(y / self.grid_size) * self.grid_size
            
            # Add component
            self.add_component(comp_type, comp_name, x, y)
            event.acceptProposedAction()
            self.update()
        else:
            event.ignore()
        
    def set_mode(self, mode: CanvasMode):
        """Set canvas operation mode"""
        self.mode = mode
        self.preview_component = None
        # Clear wire drawing state when leaving wire mode
        if mode != CanvasMode.DRAW_WIRE:
            self.wire_mode_start_node = None
            self.wire_preview = None
        self.update()
    
    def set_preview_component(self, comp_type: str, name: str):
        """Set component to preview when placing"""
        if comp_type:
            self.preview_component = CanvasComponent(
                x=0, y=0, comp_id="preview",
                comp_type=comp_type, name=name
            )
            self.mode = CanvasMode.PLACE_COMPONENT
        else:
            self.preview_component = None
            self.mode = CanvasMode.SELECT
    
    def add_component(self, comp_type: str, name: str, x: float, y: float) -> str:
        """Add component to canvas"""
        comp_id = f"comp_{len(self.components)}"
        
        # Load properties from library if available
        properties = {}
        try:
            properties = self._load_library_properties(comp_type, name)
        except:
            pass  # Use empty properties if library not available
        
        self.components[comp_id] = CanvasComponent(
            x=x, y=y, comp_id=comp_id,
            comp_type=comp_type, name=name,
            properties=properties
        )
        # Add nodes for component
        self._add_component_nodes(comp_id)
        self.component_placed.emit(comp_id, x, y)
        self.circuit_changed.emit()
        return comp_id
    
    def _load_library_properties(self, comp_type: str, comp_name: str) -> Dict:
        """Load component properties from library files"""
        import json
        from pathlib import Path
        
        # Map component types to library files
        library_map = {
            "Resistor": "resistors.json",
            "Capacitor": "capacitors.json",
            "Inductor": "inductors.json",
            "Diode": "diodes.json",
            "BJT": "transistors.json",
            "OpAmp": "analog_ics.json",
            "VoltageSource": "sources.json",
            "CurrentSource": "sources.json",
        }
        
        lib_file = library_map.get(comp_type)
        if not lib_file:
            return {}
        
        lib_path = Path(__file__).parent.parent.parent / "data" / "libraries" / lib_file
        
        try:
            with open(lib_path, 'r') as f:
                lib_data = json.load(f)
                
            # Find the component in the library
            for comp in lib_data.get("components", []):
                if comp.get("name", "").lower() == comp_name.lower() or \
                   comp.get("id", "").lower() == comp_type.lower():
                    return comp.get("properties", {})
        except:
            pass
        
        return {}
    
    def _add_component_nodes(self, comp_id: str):
        """Add connection nodes for component"""
        comp = self.components[comp_id]
        # Remove old nodes for this component first
        nodes_to_remove = [nid for nid, cid in self.node_to_component.items() if cid == comp_id]
        for nid in nodes_to_remove:
            if nid in self.nodes:
                del self.nodes[nid]
            if nid in self.node_to_component:
                del self.node_to_component[nid]
        
        # Add new nodes based on current port configuration
        ports = comp.get_ports()
        for i, (px, py) in enumerate(ports):
            node_id = f"node_{self.node_counter}"
            self.nodes[node_id] = Node(px, py, node_id)
            self.node_to_component[node_id] = comp_id  # Track which component owns this node
            self.node_counter += 1
    
    def add_wire(self, from_node: str, to_node: str):
        """Add wire between nodes with undo support"""
        if from_node in self.nodes and to_node in self.nodes:
            self.save_state()  # Save for undo
            wire_id = f"wire_{self.wire_counter}"
            self.wires[wire_id] = Wire(from_node, to_node, wire_id)
            self.wire_counter += 1
            self.circuit_changed.emit()
            self.update()
            return wire_id
        return None
    
    def refresh_all_component_nodes(self):
        """Refresh all component nodes - useful when port definitions change"""
        comp_ids = list(self.components.keys())
        for comp_id in comp_ids:
            self._add_component_nodes(comp_id)
        self.update()
    
    def get_node_at(self, x: float, y: float, tolerance: float = 15) -> Optional[str]:
        """Get node ID at position with improved snap detection"""
        closest_node = None
        closest_distance = tolerance
        
        # Find the closest node within tolerance
        for node_id, node in self.nodes.items():
            distance = node.distance_to(x, y)
            if distance < closest_distance:
                closest_node = node_id
                closest_distance = distance
        
        return closest_node
    
    def get_component_at(self, x: float, y: float) -> Optional[str]:
        """Get component ID at position"""
        for comp_id, comp in self.components.items():
            if comp.contains_point(x, y):
                return comp_id
        return None
    
    def select_component(self, comp_id: Optional[str]):
        """Select component"""
        if self.selected_component and self.selected_component in self.components:
            self.components[self.selected_component].selected = False
        
        self.selected_component = comp_id
        if comp_id and comp_id in self.components:
            self.components[comp_id].selected = True
            self.component_selected.emit(comp_id)
        self.update()
    
    def move_component(self, comp_id: str, dx: float, dy: float):
        """Move component with optional snap-to-grid"""
        if comp_id in self.components:
            comp = self.components[comp_id]
            new_x = comp.x + dx
            new_y = comp.y + dy
            
            # Snap to grid if enabled
            if self.snap_to_grid:
                new_x = round(new_x / self.grid_size) * self.grid_size
                new_y = round(new_y / self.grid_size) * self.grid_size
            
            comp.x = new_x
            comp.y = new_y
            
            # Update associated nodes
            for node_id, node in self.nodes.items():
                if self._node_belongs_to_component(node_id, comp_id):
                    node.x = new_x
                    node.y = new_y
            
            self.circuit_changed.emit()
    
    def rotate_component(self, comp_id: str, degrees: float = 90):
        """Rotate component by specified degrees"""
        if comp_id in self.components:
            comp = self.components[comp_id]
            comp.rotation = (comp.rotation + degrees) % 360
            self.circuit_changed.emit()
            self.update()
    
    def set_wire_width(self, width: int):
        """Set the width of wires drawn"""
        self.wire_width = max(1, min(width, 10))  # Clamp between 1 and 10
        self.update()
    
    def rotate_selected(self, degrees: float = 90):
        """Rotate selected component(s)"""
        if self.selected_component:
            self.rotate_component(self.selected_component, degrees)
        elif self.selected_components:
            for comp_id in self.selected_components:
                self.rotate_component(comp_id, degrees)
    
    def align_components(self, alignment: str):
        """Align selected components (left, center, right, top, middle, bottom)"""
        if len(self.selected_components) < 2:
            return
        
        comps = [self.components[cid] for cid in self.selected_components]
        
        if alignment == "left":
            min_x = min(c.x for c in comps)
            for comp in comps:
                comp.x = min_x
        
        elif alignment == "center":
            avg_x = sum(c.x for c in comps) / len(comps)
            for comp in comps:
                comp.x = avg_x
        
        elif alignment == "right":
            max_x = max(c.x for c in comps)
            for comp in comps:
                comp.x = max_x
        
        elif alignment == "top":
            min_y = min(c.y for c in comps)
            for comp in comps:
                comp.y = min_y
        
        elif alignment == "middle":
            avg_y = sum(c.y for c in comps) / len(comps)
            for comp in comps:
                comp.y = avg_y
        
        elif alignment == "bottom":
            max_y = max(c.y for c in comps)
            for comp in comps:
                comp.y = max_y
        
        # Update node positions
        for comp_id in self.selected_components:
            self._update_component_nodes(comp_id)
        
        self.circuit_changed.emit()
        self.update()
    
    def _update_component_nodes(self, comp_id: str):
        """Update node positions after component move/align"""
        comp = self.components[comp_id]
        ports = comp.get_ports()
        node_idx = 0
        for node_id, associated_comp_id in list(self.node_to_component.items()):
            if associated_comp_id == comp_id and node_idx < len(ports):
                self.nodes[node_id].x = ports[node_idx][0]
                self.nodes[node_id].y = ports[node_idx][1]
                node_idx += 1
    
    def group_components(self, comp_ids: List[str]) -> Optional[str]:
        """Group components together"""
        if len(comp_ids) < 2:
            return None
        
        # Check if all components exist
        if not all(cid in self.components for cid in comp_ids):
            return None
        
        group_id = f"group_{self.group_counter}"
        self.group_counter += 1
        self.groups[group_id] = comp_ids
        
        # Assign group ID to components
        for comp_id in comp_ids:
            self.components[comp_id].group_id = group_id
        
        return group_id
    
    def ungroup_components(self, group_id: str):
        """Ungroup components"""
        if group_id in self.groups:
            comp_ids = self.groups[group_id]
            for comp_id in comp_ids:
                if comp_id in self.components:
                    self.components[comp_id].group_id = None
            del self.groups[group_id]
            self.circuit_changed.emit()
    
    def move_group(self, group_id: str, dx: float, dy: float):
        """Move entire group of components"""
        if group_id in self.groups:
            for comp_id in self.groups[group_id]:
                self.move_component(comp_id, dx, dy)
    
    def select_multi(self, comp_id: str, toggle: bool = False):
        """Multi-select components"""
        if toggle:
            if comp_id in self.selected_components:
                self.selected_components.remove(comp_id)
                self.components[comp_id].selected = False
            else:
                self.selected_components.append(comp_id)
                self.components[comp_id].selected = True
        else:
            # Clear previous selection
            for cid in self.selected_components:
                self.components[cid].selected = False
            self.selected_components = [comp_id]
            self.components[comp_id].selected = True
        
        self.update()
    
    def _node_belongs_to_component(self, node_id: str, comp_id: str) -> bool:
        """Check if node belongs to component"""
        node = self.nodes[node_id]
        comp = self.components[comp_id]
        ports = comp.get_ports()
        for px, py in ports:
            if abs(node.x - px) < 1 and abs(node.y - py) < 1:
                return True
        return False
    
    def clear_canvas(self):
        """Clear all components and wires"""
        self.components.clear()
        self.nodes.clear()
        self.wires.clear()
        self.node_to_component.clear()
        self.selected_component = None
        self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        pos = event.pos()
        x, y = pos.x(), pos.y()
        
        # Right-click context menu
        if event.button() == Qt.RightButton:
            comp_id = self.get_component_at(x, y)
            if comp_id:
                self.show_context_menu(comp_id, pos)
            return
        
        if event.button() != Qt.LeftButton:
            return
        
        # Always check for node click first (wiring is always active)
        node_id = self.get_node_at(x, y, tolerance=15)
        if node_id:
            if not self.wire_mode_start_node:
                self.wire_mode_start_node = node_id
                self.update()
                return
            elif node_id != self.wire_mode_start_node:  # Prevent self-connection
                self.add_wire(self.wire_mode_start_node, node_id)
                self.wire_mode_start_node = None
                self.wire_preview = None
                return
        
        # Then check for component click (selection/dragging)
        comp_id = self.get_component_at(x, y)
        
        if self.mode == CanvasMode.SELECT:
            if event.modifiers() & Qt.ControlModifier:
                self.select_multi(comp_id, toggle=True)
            else:
                self.select_component(comp_id)
            
            if comp_id:
                self.dragging = True
                self.drag_start = pos
        
        elif self.mode == CanvasMode.MARQUEE:
            self.marquee_start = pos
            self.marquee_mode = True
            if not (event.modifiers() & Qt.ControlModifier):
                self.clear_selection()
        
        elif self.mode == CanvasMode.PLACE_COMPONENT:
            if self.preview_component:
                x_snap = round(x / self.grid_size) * self.grid_size if self.snap_to_grid else x
                y_snap = round(y / self.grid_size) * self.grid_size if self.snap_to_grid else y
                self.add_component(
                    self.preview_component.comp_type,
                    self.preview_component.name,
                    x_snap, y_snap
                )
                self.mode = CanvasMode.SELECT
    
    def show_context_menu(self, comp_id: str, pos: QPoint):
        """Show right-click context menu for component"""
        menu = QMenu()
        
        # Properties action
        prop_action = menu.addAction("Properties")
        prop_action.triggered.connect(lambda: self._on_properties(comp_id))
        
        menu.addSeparator()
        
        # Edit actions
        cut_action = menu.addAction("Cut")
        cut_action.triggered.connect(lambda: self._on_cut(comp_id))
        
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(lambda: self._on_copy(comp_id))
        
        paste_action = menu.addAction("Paste")
        paste_action.triggered.connect(self._on_paste)
        
        menu.addSeparator()
        
        # Transform actions
        rotate_action = menu.addAction("Rotate 90°")
        rotate_action.triggered.connect(lambda: self.rotate_component(comp_id, 90))
        
        # Resize submenu
        resize_menu = menu.addMenu("Resize")
        small_action = resize_menu.addAction("Small")
        small_action.triggered.connect(lambda: self._on_resize(comp_id, 0.7))
        medium_action = resize_menu.addAction("Medium")
        medium_action.triggered.connect(lambda: self._on_resize(comp_id, 1.0))
        large_action = resize_menu.addAction("Large")
        large_action.triggered.connect(lambda: self._on_resize(comp_id, 1.4))
        
        menu.addSeparator()
        
        # Delete action
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self._on_delete(comp_id))
        
        # Show menu at cursor position
        menu.exec(self.mapToGlobal(pos))
    
    def _on_properties(self, comp_id: str):
        """Handle properties action"""
        if comp_id in self.components:
            comp = self.components[comp_id]
            self.component_selected.emit(comp_id)
            
            # Show properties dialog
            dialog = PropertiesDialog(
                self, 
                comp.name, 
                comp.comp_type,
                comp.params if comp.params else {}
            )
            
            if dialog.exec() == PropertiesDialog.Accepted:
                # Update component properties
                comp.params = dialog.get_properties()
                self.circuit_changed.emit()
                self.update()
    
    def _on_cut(self, comp_id: str):
        """Handle cut action"""
        if comp_id in self.components:
            self.clipboard["components"] = [self.components[comp_id]]
            del self.components[comp_id]
            self.circuit_changed.emit()
            self.update()
    
    def _on_copy(self, comp_id: str):
        """Handle copy action"""
        if comp_id in self.components:
            self.clipboard["components"] = [self.components[comp_id]]
    
    def _on_paste(self):
        """Handle paste action"""
        if self.clipboard["components"]:
            for comp in self.clipboard["components"]:
                new_comp = CanvasComponent(
                    x=comp.x + 20, y=comp.y + 20,
                    comp_id=f"comp_{len(self.components)}",
                    comp_type=comp.comp_type,
                    name=comp.name,
                    params=comp.params.copy() if comp.params else {}
                )
                self.components[new_comp.comp_id] = new_comp
                self._add_component_nodes(new_comp.comp_id)
            self.circuit_changed.emit()
            self.update()
    
    def _on_resize(self, comp_id: str, scale: float):
        """Handle resize action"""
        if comp_id in self.components:
            comp = self.components[comp_id]
            comp.width *= scale
            comp.height *= scale
            self._update_component_nodes(comp_id)
            self.circuit_changed.emit()
            self.update()
    
    def _on_delete(self, comp_id: str):
        """Handle delete action"""
        if comp_id in self.components:
            # Get associated nodes
            nodes_to_delete = [nid for nid, cid in self.node_to_component.items() if cid == comp_id]
            
            # Remove wires connected to these nodes
            wires_to_delete = []
            for wire in self.wires:
                if wire[0] in nodes_to_delete or wire[1] in nodes_to_delete:
                    wires_to_delete.append(wire)
            
            for wire in wires_to_delete:
                if wire in self.wires:
                    self.wires.remove(wire)
            
            # Remove nodes
            for node_id in nodes_to_delete:
                if node_id in self.nodes:
                    del self.nodes[node_id]
                if node_id in self.node_to_component:
                    del self.node_to_component[node_id]
            
            # Remove component
            if comp_id in self.components:
                del self.components[comp_id]
            
            if self.selected_component == comp_id:
                self.selected_component = None
            
            self.circuit_changed.emit()
            self.update()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move - smooth component dragging and marquee selection"""
        pos = event.pos()
        
        if self.mode == CanvasMode.MARQUEE and self.marquee_mode and self.marquee_start:
            # Draw marquee selection box
            self.marquee_rect = QRect(self.marquee_start, pos).normalized()
            self.update()
        
        elif self.mode == CanvasMode.PLACE_COMPONENT and self.preview_component:
            self.preview_component.x = pos.x()
            self.preview_component.y = pos.y()
            self.update()
        
        elif self.mode == CanvasMode.DRAW_WIRE and self.wire_mode_start_node:
            # Show preview line from start node to current cursor position
            start_node = self.nodes[self.wire_mode_start_node]
            self.wire_preview = ((start_node.x, start_node.y), (pos.x(), pos.y()))
            self.update()
        
        elif self.dragging and self.selected_component:
            # Calculate delta movement
            delta_x = pos.x() - self.drag_start.x()
            delta_y = pos.y() - self.drag_start.y()
            
            # Move the component smoothly
            comp = self.components.get(self.selected_component)
            if comp:
                new_x = comp.x + delta_x
                new_y = comp.y + delta_y
                
                # Snap to grid if enabled
                if self.snap_to_grid:
                    new_x = round(new_x / self.grid_size) * self.grid_size
                    new_y = round(new_y / self.grid_size) * self.grid_size
                
                comp.x = new_x
                comp.y = new_y
                
                # Update nodes position
                self._update_component_nodes(self.selected_component)
            
            # Update drag start for next movement
            self.drag_start = pos
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if self.mode == CanvasMode.MARQUEE and self.marquee_mode and self.marquee_rect:
            # Select all components within marquee rect
            for comp_id, comp in self.components.items():
                if self.marquee_rect.contains(int(comp.x), int(comp.y)):
                    if event.modifiers() & Qt.ControlModifier:
                        self.select_multi(comp_id, toggle=False)
                    else:
                        self.select_component(comp_id)
            self.marquee_mode = False
            self.marquee_start = None
            self.marquee_rect = None
            self.update()
        
        self.dragging = False
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        self.zoom_level *= zoom_factor
        self.zoom_level = max(0.1, min(self.zoom_level, 5.0))
        self.update()
    
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key_Delete:
            if self.selected_component and self.selected_component not in self.selected_components:
                comp_id = self.selected_component
                del self.components[comp_id]
                self.selected_component = None
                self.circuit_changed.emit()
            elif self.selected_components:
                for comp_id in self.selected_components:
                    del self.components[comp_id]
                self.selected_components = []
            self.update()
        
        elif event.key() == Qt.Key_Escape:
            self.set_mode(CanvasMode.SELECT)
            self.select_component(None)
        
        elif event.key() == Qt.Key_R:  # Rotate
            self.rotate_selected(90)
        
        elif event.key() == Qt.Key_G and self.selected_components:  # Group
            self.group_components(self.selected_components)
            self.circuit_changed.emit()
        
        elif event.key() == Qt.Key_U and self.selected_component:  # Ungroup
            comp = self.components.get(self.selected_component)
            if comp and comp.group_id:
                self.ungroup_components(comp.group_id)
                self.update()
    
    def paintEvent(self, event):
        """Render canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor("#f5f5f5"))
        
        # Draw grid
        if self.show_grid:
            self._draw_grid(painter)
        
        # Draw wires
        for wire in self.wires.values():
            self._draw_wire(painter, wire)
        
        # Draw wire preview (while drawing new wire) with enhanced styling
        if self.wire_preview:
            (x1, y1), (x2, y2) = self.wire_preview
            # Dashed orange line for preview
            painter.setPen(QPen(QColor("#ff9800"), 3, Qt.DashLine))
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            # Add circle at end point
            painter.setPen(QPen(QColor("#ff9800"), 2))
            painter.setBrush(QBrush(QColor("#ffff00")))
            painter.drawEllipse(int(x2-5), int(y2-5), 10, 10)
        
        # Draw preview component
        if self.preview_component:
            self._draw_component(painter, self.preview_component, preview=True)
        
        # Draw components
        for comp in self.components.values():
            self._draw_component(painter, comp)
        
        # Draw nodes
        for node in self.nodes.values():
            self._draw_node(painter, node)
        
        # Draw marquee selection box
        if self.marquee_rect and self.marquee_mode:
            painter.setPen(QPen(QColor("#0066cc"), 2, Qt.DashLine))
            painter.setBrush(QBrush(QColor(0, 102, 204, 30)))  # Semi-transparent blue
            painter.drawRect(self.marquee_rect)
    
    def _draw_grid(self, painter: QPainter):
        """Draw grid background"""
        painter.setPen(QPen(QColor("#e0e0e0"), 1))
        
        for x in range(0, self.width(), self.grid_size):
            painter.drawLine(x, 0, x, self.height())
        
        for y in range(0, self.height(), self.grid_size):
            painter.drawLine(0, y, self.width(), y)
    
    def _draw_component(self, painter: QPainter, comp: CanvasComponent, preview: bool = False):
        """Draw component symbol with rotation support"""
        painter.save()
        
        x, y = int(comp.x), int(comp.y)
        
        # Apply rotation
        if comp.rotation != 0:
            painter.translate(x, y)
            painter.rotate(comp.rotation)
            painter.translate(-x, -y)
        
        # Select symbol based on component name (case-insensitive)
        comp_name_lower = comp.name.lower()
        
        if "resistor" in comp_name_lower:
            self._draw_resistor(painter, x, y, comp.selected)
        elif "capacitor" in comp_name_lower:
            self._draw_capacitor(painter, x, y, comp.selected)
        elif "inductor" in comp_name_lower:
            self._draw_inductor(painter, x, y, comp.selected)
        elif "diode" in comp_name_lower:
            self._draw_diode(painter, x, y, comp.selected)
        elif "battery" in comp_name_lower:
            self._draw_battery(painter, x, y, comp.selected)
        elif "ac source" in comp_name_lower or "ac" in comp_name_lower:
            self._draw_ac_source(painter, x, y, comp.selected)
        elif "dc source" in comp_name_lower or "voltage" in comp_name_lower:
            self._draw_dc_source(painter, x, y, comp.selected)
        elif "current source" in comp_name_lower:
            self._draw_current_source(painter, x, y, comp.selected)
        elif "ground" in comp_name_lower:
            self._draw_ground(painter, x, y, comp.selected)
        elif "switch" in comp_name_lower:
            self._draw_switch(painter, x, y, comp.selected)
        elif "relay" in comp_name_lower:
            self._draw_relay(painter, x, y, comp.selected)
        elif "transformer" in comp_name_lower:
            self._draw_transformer(painter, x, y, comp.selected)
        elif "motor" in comp_name_lower:
            self._draw_motor(painter, x, y, comp.selected)
        elif "generator" in comp_name_lower:
            self._draw_generator(painter, x, y, comp.selected)
        elif "ammeter" in comp_name_lower:
            self._draw_ammeter(painter, x, y, comp.selected)
        elif "voltmeter" in comp_name_lower:
            self._draw_voltmeter(painter, x, y, comp.selected)
        elif "wattmeter" in comp_name_lower:
            self._draw_wattmeter(painter, x, y, comp.selected)
        elif "ohmmeter" in comp_name_lower:
            self._draw_ohmmeter(painter, x, y, comp.selected)
        elif "thyristor" in comp_name_lower:
            self._draw_thyristor(painter, x, y, comp.selected)
        elif "bjt" in comp_name_lower:
            self._draw_bjt(painter, x, y, comp.selected)
        elif "mosfet" in comp_name_lower:
            self._draw_mosfet(painter, x, y, comp.selected)
        elif "led" in comp_name_lower:
            self._draw_led(painter, x, y, comp.selected)
        elif "op-amp" in comp_name_lower or "opamp" in comp_name_lower:
            self._draw_opamp(painter, x, y, comp.selected)
        elif "multiplexer" in comp_name_lower or "mux" in comp_name_lower:
            self._draw_multiplexer(painter, x, y, comp.selected)
        elif "demultiplexer" in comp_name_lower or "demux" in comp_name_lower:
            self._draw_demultiplexer(painter, x, y, comp.selected)
        elif "variable resistor" in comp_name_lower:
            self._draw_variable_resistor(painter, x, y, comp.selected)
        elif "potentiometer" in comp_name_lower:
            self._draw_potentiometer(painter, x, y, comp.selected)
        elif "fuse" in comp_name_lower:
            self._draw_fuse(painter, x, y, comp.selected)
        elif "circuit breaker" in comp_name_lower:
            self._draw_circuit_breaker(painter, x, y, comp.selected)
        elif "rectifier" in comp_name_lower:
            self._draw_rectifier(painter, x, y, comp.selected)
        elif "filter" in comp_name_lower:
            self._draw_filter(painter, x, y, comp.selected)
        elif "multimeter" in comp_name_lower:
            self._draw_multimeter(painter, x, y, comp.selected)
        elif "voltage divider" in comp_name_lower:
            self._draw_voltage_divider(painter, x, y, comp.selected)
        elif "connector" in comp_name_lower or "plug" in comp_name_lower or "socket" in comp_name_lower or "wire" in comp_name_lower:
            self._draw_connector(painter, x, y, comp.name, comp.selected)
        elif "contactor" in comp_name_lower:
            self._draw_contactor(painter, x, y, comp.selected)
        elif "push button" in comp_name_lower:
            self._draw_push_button(painter, x, y, comp.selected)
        elif "zener" in comp_name_lower or "schottky" in comp_name_lower:
            self._draw_diode(painter, x, y, comp.selected)  # Similar to diode
        elif "stepper" in comp_name_lower:
            self._draw_motor(painter, x, y, comp.selected)  # Similar to motor
        elif "ac motor" in comp_name_lower:
            self._draw_motor(painter, x, y, comp.selected)
        elif "dc motor" in comp_name_lower:
            self._draw_motor(painter, x, y, comp.selected)
        elif "thermistor" in comp_name_lower:
            self._draw_resistor(painter, x, y, comp.selected)  # Similar to resistor
        elif "sensor" in comp_name_lower or "photo diode" in comp_name_lower:
            self._draw_photo_sensor(painter, x, y, comp.selected)
        elif "terminal" in comp_name_lower or "bus bar" in comp_name_lower:
            self._draw_terminal_block(painter, x, y, comp.selected)
        elif "ic" in comp_name_lower or "op-amp" in comp_name_lower or "timer" in comp_name_lower or "741" in comp_name_lower or "microcontroller" in comp_name_lower or "processor" in comp_name_lower or "ram" in comp_name_lower or "rom" in comp_name_lower or "dsp" in comp_name_lower or "fpga" in comp_name_lower:
            self._draw_ic_dip(painter, x, y, comp.selected, comp.name)
        elif "gate" in comp_name_lower or "logic" in comp_name_lower:
            self._draw_logic_gate(painter, x, y, comp.selected, comp.name)
        elif "antenna" in comp_name_lower:
            self._draw_antenna(painter, x, y, comp.selected)
        elif "crystal" in comp_name_lower or "oscillator" in comp_name_lower:
            self._draw_crystal(painter, x, y, comp.selected)
        elif "display" in comp_name_lower or "7-segment" in comp_name_lower or "lcd" in comp_name_lower:
            self._draw_display(painter, x, y, comp.selected, comp.name)
        elif "solenoid" in comp_name_lower or "electromagnet" in comp_name_lower:
            self._draw_solenoid(painter, x, y, comp.selected)
        elif "buzzer" in comp_name_lower or "speaker" in comp_name_lower:
            self._draw_speaker(painter, x, y, comp.selected)
        elif "varistor" in comp_name_lower or "varactor" in comp_name_lower:
            self._draw_varistor(painter, x, y, comp.selected)
        elif "jfet" in comp_name_lower:
            self._draw_jfet(painter, x, y, comp.selected)
        elif "igbt" in comp_name_lower:
            self._draw_igbt(painter, x, y, comp.selected)
        elif "triac" in comp_name_lower:
            self._draw_triac(painter, x, y, comp.selected)
        elif "comparator" in comp_name_lower:
            self._draw_comparator(painter, x, y, comp.selected)
        else:
            self._draw_generic_component(painter, x, y, comp.name, comp.selected)
        
        # Draw component name label (always visible when selected or on hover)
        if comp.selected:
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            painter.setPen(QPen(QColor("#ff6600")))
            # Display name above component
            name_text = f"{comp.name}"
            painter.drawText(int(x-40), int(y-35), 80, 15, Qt.AlignCenter, name_text)
        
        painter.restore()
    
    def _draw_resistor(self, painter, x, y, selected):
        """Draw resistor symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        points = [(x-25, y), (x-18, y-6), (x-12, y+6), (x-6, y-6), (x, y+6), (x+6, y-6), (x+12, y+6), (x+22, y)]
        for i in range(len(points)-1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        painter.drawLine(x-30, y, x-25, y)
        painter.drawLine(x+22, y, x+30, y)
        painter.setFont(QFont("Arial", 7))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-10, y+12, 20, 10, Qt.AlignCenter, "R")
    
    def _draw_capacitor(self, painter, x, y, selected):
        """Draw capacitor symbol - improved"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        # Left wire
        painter.drawLine(x-30, y, x-15, y)
        # Right wire
        painter.drawLine(x+15, y, x+30, y)
        # Two parallel plates (top and bottom)
        painter.drawLine(x-15, y-12, x-15, y+12)
        painter.drawLine(x+15, y-12, x+15, y+12)
        # Label
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-8, y+15, 16, 10, Qt.AlignCenter, "C")
    
    def _draw_inductor(self, painter, x, y, selected):
        """Draw inductor symbol - improved coil representation"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-22, y)
        painter.drawLine(x+22, y, x+30, y)
        # Draw coil loops
        for i in range(5):
            painter.drawArc(x-20+i*8, y-6, 8, 12, 0, 180*16)
        # Label
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-6, y+15, 12, 10, Qt.AlignCenter, "L")
    
    def _draw_diode(self, painter, x, y, selected):
        """Draw diode symbol"""
        color = QColor("#ff9800") if selected else QColor("#cc0000")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#ffcccc")))
        painter.drawLine(x-30, y, x-15, y)
        painter.drawLine(x+15, y, x+30, y)
        tri = QPolygon([QPoint(x-12, y-10), QPoint(x-12, y+10), QPoint(x+10, y)])
        painter.drawPolygon(tri)
        painter.drawLine(x+10, y-12, x+10, y+12)
        painter.setFont(QFont("Arial", 7))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-8, y+12, 16, 10, Qt.AlignCenter, "D")
    
    def _draw_battery(self, painter, x, y, selected):
        """Draw battery symbol"""
        color = QColor("#ff9800") if selected else QColor("#000000")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        # Positive terminal (long line)
        painter.drawLine(x+10, y-12, x+10, y+12)
        # Negative terminal (short line)
        painter.drawLine(x-8, y-8, x-8, y+8)
        painter.setFont(QFont("Arial", 7))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-8, y+12, 16, 10, Qt.AlignCenter, "B")
    
    def _draw_ac_source(self, painter, x, y, selected):
        """Draw AC source symbol"""
        color = QColor("#ff9800") if selected else QColor("#0066cc")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#e3f2fd")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawEllipse(x-14, y-14, 28, 28)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(QPen(QColor("#0066cc")))
        painter.drawText(x-8, y-8, 16, 16, Qt.AlignCenter, "~")
    
    def _draw_dc_source(self, painter, x, y, selected):
        """Draw DC source symbol"""
        color = QColor("#ff9800") if selected else QColor("#0066cc")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#e3f2fd")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawEllipse(x-14, y-14, 28, 28)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(QPen(QColor("#0066cc")))
        painter.drawText(x-6, y-6, 12, 12, Qt.AlignCenter, "+")
        painter.drawText(x-6, y+2, 12, 12, Qt.AlignCenter, "-")
    
    def _draw_current_source(self, painter, x, y, selected):
        """Draw current source symbol"""
        color = QColor("#ff9800") if selected else QColor("#009900")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#e3ffe3")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawEllipse(x-14, y-14, 28, 28)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(QPen(QColor("#009900")))
        painter.drawText(x-4, y-6, 8, 12, Qt.AlignCenter, "I")
    
    def _draw_ground(self, painter, x, y, selected):
        """Draw ground symbol with single top connection point"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        
        # Top vertical line (connection point)
        painter.drawLine(x, y-15, x, y-2)
        
        # Horizontal lines (ground symbol)
        painter.drawLine(x-12, y, x+12, y)
        painter.drawLine(x-9, y+5, x+9, y+5)
        painter.drawLine(x-6, y+10, x+6, y+10)
        
        # Draw connection node indicator at top
        if selected:
            painter.setBrush(QBrush(QColor("#ff9800")))
            painter.drawEllipse(QPointF(x, y-15), 3, 3)
    
    def _draw_switch(self, painter, x, y, selected):
        """Draw switch symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-15, y)
        painter.drawLine(x+15, y, x+30, y)
        painter.drawLine(x-15, y, x+5, y+8)
        painter.drawEllipse(x+5-3, y+8-3, 6, 6)
    
    def _draw_relay(self, painter, x, y, selected):
        """Draw relay symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawRect(x-18, y-12, 36, 24)
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawLine(x-10, y-15, x+10, y-15)
    
    def _draw_transformer(self, painter, x, y, selected):
        """Draw transformer symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-20, y)
        painter.drawLine(x+20, y, x+30, y)
        for i in range(3):
            painter.drawArc(x-22, y-8+i*8, 8, 8, 0, 360*16)
            painter.drawArc(x+14, y-8+i*8, 8, 8, 0, 360*16)
    
    def _draw_motor(self, painter, x, y, selected):
        """Draw motor symbol"""
        color = QColor("#ff9800") if selected else QColor("#009999")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#ccffff")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawEllipse(x-14, y-14, 28, 28)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.setPen(QPen(color))
        painter.drawText(x-6, y-8, 12, 16, Qt.AlignCenter, "M")
    
    def _draw_generator(self, painter, x, y, selected):
        """Draw generator symbol"""
        color = QColor("#ff9800") if selected else QColor("#669900")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#ffffcc")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawEllipse(x-14, y-14, 28, 28)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.setPen(QPen(color))
        painter.drawText(x-6, y-8, 12, 16, Qt.AlignCenter, "G")
    
    def _draw_ammeter(self, painter, x, y, selected):
        """Draw ammeter symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#f0f0f0")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawEllipse(x-14, y-14, 28, 28)
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-8, y-6, 16, 12, Qt.AlignCenter, "A")
    
    def _draw_voltmeter(self, painter, x, y, selected):
        """Draw voltmeter symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#f0f0f0")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawEllipse(x-14, y-14, 28, 28)
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-8, y-6, 16, 12, Qt.AlignCenter, "V")
    
    def _draw_wattmeter(self, painter, x, y, selected):
        """Draw wattmeter symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#f0f0f0")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawEllipse(x-14, y-14, 28, 28)
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-8, y-6, 16, 12, Qt.AlignCenter, "W")
    
    def _draw_ohmmeter(self, painter, x, y, selected):
        """Draw ohmmeter symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#f0f0f0")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawEllipse(x-14, y-14, 28, 28)
        painter.setFont(QFont("Arial", 7, QFont.Bold))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-8, y-6, 16, 12, Qt.AlignCenter, "Ω")
    
    def _draw_bjt(self, painter, x, y, selected):
        """Draw BJT symbol"""
        color = QColor("#ff9800") if selected else QColor("#cc0066")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y-10, x-10, y-10)  # Collector
        painter.drawLine(x-30, y, x-20, y)  # Base
        painter.drawLine(x-30, y+10, x-10, y+10)  # Emitter
        painter.drawRect(x-10, y-8, 8, 16)
        painter.drawLine(x-2, y-10, x+10, y-10)
        painter.drawLine(x-2, y+10, x+6, y+14)
        painter.drawLine(x+6, y+10, x+10, y+16)
    
    def _draw_mosfet(self, painter, x, y, selected):
        """Draw MOSFET symbol"""
        color = QColor("#ff9800") if selected else QColor("#cc0066")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y-10, x-10, y-10)  # Drain
        painter.drawLine(x-30, y, x-20, y)  # Gate
        painter.drawLine(x-30, y+10, x-10, y+10)  # Source
        painter.drawRect(x-8, y-8, 6, 16)
        painter.drawLine(x-2, y-10, x+10, y-10)
        painter.drawLine(x-2, y+10, x+10, y+10)
    
    def _draw_thyristor(self, painter, x, y, selected):
        """Draw thyristor symbol"""
        color = QColor("#ff9800") if selected else QColor("#990099")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y-10, x-10, y-10)
        painter.drawLine(x-30, y, x-20, y)
        painter.drawLine(x-30, y+10, x-10, y+10)
        painter.drawPolygon(QPolygon([QPoint(x-8, y-8), QPoint(x-8, y+8), QPoint(x+8, y)]))
        painter.drawLine(x+8, y-8, x+12, y-12)
    
    def _draw_contactor(self, painter, x, y, selected):
        """Draw contactor symbol (coil with contacts)"""
        color = QColor("#ff9800") if selected else QColor("#0066cc")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        # Coil representation
        painter.drawLine(x-30, y, x-15, y)
        painter.drawEllipse(x-12, y-10, 10, 10)
        painter.drawEllipse(x-2, y-10, 10, 10)
        painter.drawLine(x+8, y, x+30, y)
    
    def _draw_push_button(self, painter, x, y, selected):
        """Draw push button symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-15, y)
        painter.drawLine(x+15, y, x+30, y)
        # Button representation
        painter.drawCircle(x, y-8, 8)
        painter.drawRect(x-10, y+2, 20, 10)
        painter.drawLine(x, y-8, x, y+2)
    
    def _draw_photo_sensor(self, painter, x, y, selected):
        """Draw photo diode/sensor symbol"""
        color = QColor("#ff9800") if selected else QColor("#ff0066")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-15, y)
        painter.drawLine(x+15, y, x+30, y)
        # Triangle diode with light arrows
        tri = QPolygon([QPoint(x-12, y-10), QPoint(x-12, y+10), QPoint(x+10, y)])
        painter.drawPolygon(tri)
        painter.drawLine(x+10, y-12, x+10, y+12)
        # Light arrows
        painter.drawLine(x+12, y-12, x+18, y-18)
        painter.drawLine(x+18, y-18, x+20, y-16)
        painter.drawLine(x+18, y-12, x+24, y-18)
        painter.drawLine(x+24, y-18, x+26, y-16)
    
    def _draw_terminal_block(self, painter, x, y, selected):
        """Draw terminal block/bus bar symbol"""
        color = QColor("#ff9800") if selected else QColor("#666666")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#cccccc")))
        painter.drawLine(x-30, y, x-20, y)
        painter.drawRect(x-15, y-12, 30, 24)
        painter.drawLine(x-8, y-8, x-8, y+8)
        painter.drawLine(x+2, y-8, x+2, y+8)
        painter.drawLine(x+12, y, x+30, y)
    
    def _draw_ic_dip(self, painter, x, y, selected, comp_name):
        """Draw DIP IC package (8, 14, 16, 28, 40 pin)"""
        color = QColor("#ff9800") if selected else QColor("#000080")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#e0e0e0")))
        painter.drawRect(x-20, y-20, 40, 40)
        # Draw notch (pin 1 indicator)
        painter.drawLine(x-20, y-16, x-20, y-10)
        painter.drawCircle(x-18, y-14, 2)
        # Draw pin indicators
        for i in range(4):
            painter.drawLine(x-20, y-16+i*8, x-24, y-16+i*8)
            painter.drawLine(x+20, y-16+i*8, x+24, y-16+i*8)
        painter.setFont(QFont("Arial", 7, QFont.Bold))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-15, y-5, 30, 10, Qt.AlignCenter, comp_name[:8])
    
    def _draw_logic_gate(self, painter, x, y, selected, comp_name):
        """Draw logic gate symbol"""
        color = QColor("#ff9800") if selected else QColor("#0066cc")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#e3f2fd")))
        gate_type = comp_name.lower()
        if "and" in gate_type:
            painter.drawRect(x-15, y-12, 20, 24)
            painter.drawArc(int(x+5), int(y-12), 10, 24, 0, 180*16)
        elif "or" in gate_type:
            painter.drawArc(int(x-10), int(y-12), 10, 24, 270*16, 180*16)
            painter.drawRect(x+0, y-12, 15, 24)
        elif "not" in gate_type or "inverter" in gate_type:
            tri = QPolygon([QPoint(x-15, y-12), QPoint(x-15, y+12), QPoint(x+15, y)])
            painter.drawPolygon(tri)
            painter.drawCircle(x+17, y, 3)
        else:
            painter.drawArc(int(x-15), int(y-12), 10, 24, 270*16, 180*16)
            painter.drawArc(int(x-10), int(y-12), 10, 24, 270*16, 180*16)
            painter.drawRect(x+0, y-12, 15, 24)
        painter.setFont(QFont("Arial", 6, QFont.Bold))
        painter.setPen(QPen(QColor("#000000")))
        gate_label = comp_name.replace(" Gate", "").replace(" ", "")[:4]
        painter.drawText(x-8, y-4, 16, 8, Qt.AlignCenter, gate_label)
    
    def _draw_antenna(self, painter, x, y, selected):
        """Draw antenna symbol"""
        color = QColor("#ff9800") if selected else QColor("#cc0000")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-10, y)
        painter.drawLine(x+10, y, x+30, y)
        painter.drawLine(x-5, y, x-5, y-15)
        painter.drawLine(x+0, y, x+0, y-20)
        painter.drawLine(x+5, y, x+5, y-15)
        painter.drawArc(int(x-8), int(y-15), 16, 15, 0, 180*16)
    
    def _draw_crystal(self, painter, x, y, selected):
        """Draw crystal oscillator symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-15, y)
        painter.drawLine(x+15, y, x+30, y)
        painter.drawRect(x-8, y-10, 4, 20)
        painter.drawRect(x+4, y-10, 4, 20)
        painter.drawLine(x-6, y-10, x+6, y-10)
        painter.drawLine(x-6, y+10, x+6, y+10)
    
    def _draw_display(self, painter, x, y, selected, comp_name):
        """Draw display symbol"""
        color = QColor("#ff9800") if selected else QColor("#ffaa00")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#ffffcc")))
        painter.drawRect(x-18, y-14, 36, 28)
        if "7-segment" in comp_name.lower():
            painter.drawLine(x-10, y-8, x+10, y-8)
            painter.drawLine(x-10, y+0, x+10, y+0)
            painter.drawLine(x-10, y+8, x+10, y+8)
        else:
            for i in range(4):
                for j in range(3):
                    painter.drawEllipse(int(x-8+i*5), int(y-6+j*5), 2, 2)
    
    def _draw_solenoid(self, painter, x, y, selected):
        """Draw solenoid/electromagnet symbol"""
        color = QColor("#ff9800") if selected else QColor("#0066cc")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-15, y)
        painter.drawLine(x+15, y, x+30, y)
        for i in range(4):
            painter.drawEllipse(int(x-12+i*6), int(y-8), 6, 16)
    
    def _draw_speaker(self, painter, x, y, selected):
        """Draw speaker/buzzer symbol"""
        color = QColor("#ff9800") if selected else QColor("#666666")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#cccccc")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        tri = QPolygon([QPoint(x-12, y-12), QPoint(x-12, y+12), QPoint(x, y)])
        painter.drawPolygon(tri)
        painter.drawArc(int(x+2), int(y-16), 10, 10, 0, 90*16)
        painter.drawArc(int(x+2), int(y-22), 16, 16, 0, 90*16)
    
    def _draw_varistor(self, painter, x, y, selected):
        """Draw varistor/varactor symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        points = [(x-25, y), (x-18, y-6), (x-12, y+6), (x-6, y-6), (x, y+6), (x+6, y-6), (x+12, y+6), (x+22, y)]
        for i in range(len(points)-1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        painter.drawLine(x-30, y, x-25, y)
        painter.drawLine(x+22, y, x+30, y)
        painter.drawLine(x+10, y+8, x+15, y+14)
        painter.drawLine(x+15, y+14, x+12, y+12)
        painter.drawLine(x+15, y+14, x+17, y+11)
    
    def _draw_jfet(self, painter, x, y, selected):
        """Draw JFET symbol"""
        color = QColor("#ff9800") if selected else QColor("#0066cc")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#e3f2fd")))
        painter.drawRect(x-5, y-12, 10, 24)
        painter.drawLine(x-10, y-6, x-5, y-6)
        painter.drawLine(x-10, y-6, x-12, y-8)
        painter.drawLine(x-10, y-6, x-12, y-4)
        painter.drawLine(x, y-16, x, y-20)
        painter.drawLine(x, y+16, x, y+20)
        painter.setFont(QFont("Arial", 6))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x+4, y-20, 10, 8, Qt.AlignLeft, "D")
        painter.drawText(x+4, y+18, 10, 8, Qt.AlignLeft, "S")
    
    def _draw_igbt(self, painter, x, y, selected):
        """Draw IGBT symbol"""
        color = QColor("#ff9800") if selected else QColor("#0066cc")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-15, y)
        painter.drawLine(x+15, y, x+30, y)
        painter.drawRect(x-5, y-12, 10, 24)
        painter.drawLine(x-8, y-8, x-5, y-8)
        painter.drawLine(x-8, y, x-5, y)
        painter.drawLine(x-8, y+8, x-5, y+8)
    
    def _draw_triac(self, painter, x, y, selected):
        """Draw TRIAC symbol"""
        color = QColor("#ff9800") if selected else QColor("#cc6600")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-12, y)
        painter.drawLine(x+12, y, x+30, y)
        painter.drawRect(x-8, y-10, 8, 20)
        painter.drawRect(x, y-10, 8, 20)
        painter.drawLine(x-10, y+12, x-10, y+18)
    
    def _draw_comparator(self, painter, x, y, selected):
        """Draw comparator symbol"""
        color = QColor("#ff9800") if selected else QColor("#0066cc")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#e3f2fd")))
        tri = QPolygon([QPoint(x-15, y-14), QPoint(x-15, y+14), QPoint(x+15, y)])
        painter.drawPolygon(tri)
        painter.drawLine(x-25, y-6, x-15, y-6)
        painter.drawLine(x-25, y+6, x-15, y+6)
        painter.drawLine(x+15, y, x+25, y)
        painter.setFont(QFont("Arial", 6))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-20, y-10, 8, 6, Qt.AlignCenter, "+")
        painter.drawText(x-20, y+6, 8, 6, Qt.AlignCenter, "-")
    
    def _draw_generic_component(self, painter, x, y, name, selected):
        """Draw generic component"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1))
        painter.setBrush(QBrush(QColor("#f9f9f9")))
        painter.drawRoundedRect(x-22, y-16, 44, 32, 4, 4)
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-20, y-6, 40, 12, Qt.AlignCenter, name[:10])
    
    def _draw_led(self, painter, x, y, selected):
        """Draw LED symbol (diode with arrows)"""
        color = QColor("#ff9800") if selected else QColor("#ff0000")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-15, y)
        painter.drawLine(x+15, y, x+30, y)
        tri = QPolygon([QPoint(x-12, y-10), QPoint(x-12, y+10), QPoint(x+10, y)])
        painter.drawPolygon(tri)
        painter.drawLine(x+10, y-12, x+10, y+12)
        painter.drawLine(x+10, y-12, x+15, y-18)
        painter.drawLine(x+15, y-18, x+20, y-12)
        painter.drawLine(x+20, y-12, x+25, y-18)
    
    def _draw_variable_resistor(self, painter, x, y, selected):
        """Draw variable resistor symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        points = [(x-25, y), (x-18, y-6), (x-12, y+6), (x-6, y-6), (x, y+6), (x+6, y-6), (x+12, y+6), (x+22, y)]
        for i in range(len(points)-1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        painter.drawLine(x-30, y, x-25, y)
        painter.drawLine(x+22, y, x+30, y)
        painter.drawLine(x+10, y-10, x+15, y-15)
    
    def _draw_potentiometer(self, painter, x, y, selected):
        """Draw potentiometer symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        points = [(x-25, y), (x-18, y-6), (x-12, y+6), (x-6, y-6), (x, y+6), (x+6, y-6), (x+12, y+6), (x+22, y)]
        for i in range(len(points)-1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        painter.drawLine(x-30, y, x-25, y)
        painter.drawLine(x+22, y, x+30, y)
        painter.drawLine(x+0, y-10, x+5, y-15)
    
    def _draw_fuse(self, painter, x, y, selected):
        """Draw fuse symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-15, y)
        painter.drawLine(x+15, y, x+30, y)
        painter.drawRect(x-12, y-8, 24, 16)
        painter.drawLine(x-8, y-5, x+8, y+5)
    
    def _draw_circuit_breaker(self, painter, x, y, selected):
        """Draw circuit breaker symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawRect(x-14, y-10, 28, 20)
        painter.drawLine(x, y-10, x, y+10)
    
    def _draw_rectifier(self, painter, x, y, selected):
        """Draw rectifier symbol (bridge rectifier)"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawRect(x-12, y-12, 24, 24)
        painter.drawLine(x-12, y, x+12, y)
        painter.drawLine(x, y-12, x, y+12)
    
    def _draw_filter(self, painter, x, y, selected):
        """Draw filter symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y, x-15, y)
        painter.drawLine(x+15, y, x+30, y)
        painter.drawEllipse(x-14, y-10, 28, 20)
        painter.drawLine(x-8, y-6, x-8, y+6)
        painter.drawLine(x+8, y-6, x+8, y+6)
    
    def _draw_multimeter(self, painter, x, y, selected):
        """Draw multimeter symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#f0f0f0")))
        painter.drawLine(x-30, y, x-18, y)
        painter.drawLine(x+18, y, x+30, y)
        painter.drawEllipse(x-14, y-14, 28, 28)
        painter.setFont(QFont("Arial", 7, QFont.Bold))
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(x-10, y-6, 20, 12, Qt.AlignCenter, "Ω/V")
    
    def _draw_voltage_divider(self, painter, x, y, selected):
        """Draw voltage divider symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawLine(x-30, y-8, x-15, y-8)
        painter.drawLine(x-30, y+8, x-15, y+8)
        painter.drawLine(x-15, y-8, x-15, y+8)
        points = [(x-15, y-8), (x-8, y-3), (x-1, y-8), (x+6, y-3), (x+13, y-8), (x+15, y-8)]
        for i in range(len(points)-1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        painter.drawLine(x+15, y-8, x+30, y-8)
        painter.drawLine(x+15, y+8, x+30, y+8)
    
    def _draw_opamp(self, painter, x, y, selected):
        """Draw Op-Amp symbol (triangle)"""
        color = QColor("#ff9800") if selected else QColor("#0066cc")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#e3f2fd")))
        tri = QPolygon([QPoint(x-12, y-14), QPoint(x+12, y), QPoint(x-12, y+14)])
        painter.drawPolygon(tri)
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor("#0066cc")))
        painter.drawText(x-8, y-4, 16, 8, Qt.AlignCenter, "U")
    
    def _draw_multiplexer(self, painter, x, y, selected):
        """Draw Multiplexer (MUX) symbol"""
        color = QColor("#ff9800") if selected else QColor("#0066cc")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#e3f2fd")))
        # Draw trapezoid shape (wider at top, narrower at bottom)
        mux = QPolygon([QPoint(x-16, y-12), QPoint(x+16, y-12), QPoint(x+8, y+12), QPoint(x-8, y+12)])
        painter.drawPolygon(mux)
        painter.setFont(QFont("Arial", 7, QFont.Bold))
        painter.setPen(QPen(QColor("#0066cc")))
        painter.drawText(x-10, y-5, 20, 10, Qt.AlignCenter, "MUX")
    
    def _draw_demultiplexer(self, painter, x, y, selected):
        """Draw Demultiplexer (DEMUX) symbol"""
        color = QColor("#ff9800") if selected else QColor("#006600")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.setBrush(QBrush(QColor("#e8f5e9")))
        # Draw trapezoid shape (narrower at top, wider at bottom)
        demux = QPolygon([QPoint(x-8, y-12), QPoint(x+8, y-12), QPoint(x+16, y+12), QPoint(x-16, y+12)])
        painter.drawPolygon(demux)
        painter.setFont(QFont("Arial", 7, QFont.Bold))
        painter.setPen(QPen(QColor("#006600")))
        painter.drawText(x-14, y-5, 28, 10, Qt.AlignCenter, "DEMUX")
    
    def _draw_connector(self, painter, x, y, name, selected):
        """Draw connector/wire symbol"""
        color = QColor("#ff9800") if selected else QColor("#333333")
        painter.setPen(QPen(color, 2 if selected else 1.5))
        painter.drawCircle(x-8, y, 6)
        painter.drawCircle(x+8, y, 6)
        painter.drawLine(x-8, y, x+8, y)
    
    def _draw_wire(self, painter: QPainter, wire: Wire):
        """Draw wire connection"""
        if wire.from_node in self.nodes and wire.to_node in self.nodes:
            n1 = self.nodes[wire.from_node]
            n2 = self.nodes[wire.to_node]
            painter.setPen(QPen(QColor("#000000"), self.wire_width))  # Black wire with adjustable width
            painter.drawLine(int(n1.x), int(n1.y), int(n2.x), int(n2.y))
    
    def _draw_node(self, painter: QPainter, node: Node):
        """Draw connection node with enhanced visibility"""
        # Highlight node if it's the current wire start node
        is_wire_start = hasattr(self, 'wire_mode_start_node') and node.node_id == self.wire_mode_start_node
        
        if is_wire_start:
            # Highlight start node in yellow
            painter.setPen(QPen(QColor("#ff9800"), 2))
            painter.setBrush(QBrush(QColor("#ffff00")))
            painter.drawEllipse(int(node.x - 6), int(node.y - 6), 12, 12)
        else:
            # Normal node in blue
            painter.setPen(QPen(QColor("#000000"), 1))
            painter.setBrush(QBrush(QColor("#0066cc")))
            painter.drawEllipse(int(node.x - 4), int(node.y - 4), 8, 8)

    # ============== UNDO/REDO SYSTEM ==============
    
    def save_state(self):
        """Save current state to undo stack"""
        state = {
            "components": copy.deepcopy(self.components),
            "wires": copy.deepcopy(self.wires),
            "node_to_component": copy.deepcopy(self.node_to_component),
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()  # Clear redo when new action performed
        
        # Limit undo levels to prevent memory issues
        if len(self.undo_stack) > self.max_undo_levels:
            self.undo_stack.pop(0)
        
        self.undo_redo_changed.emit(len(self.undo_stack) > 0, len(self.redo_stack) > 0)
    
    def undo(self):
        """Undo last action"""
        if self.undo_stack:
            # Save current state to redo
            state = {
                "components": copy.deepcopy(self.components),
                "wires": copy.deepcopy(self.wires),
                "node_to_component": copy.deepcopy(self.node_to_component),
            }
            self.redo_stack.append(state)
            
            # Restore from undo stack
            prev_state = self.undo_stack.pop()
            self.components = prev_state["components"]
            self.wires = prev_state["wires"]
            self.node_to_component = prev_state["node_to_component"]
            self.selected_component = None
            self.selected_components = []
            
            self.undo_redo_changed.emit(len(self.undo_stack) > 0, len(self.redo_stack) > 0)
            self.circuit_changed.emit()
            self.update()
    
    def redo(self):
        """Redo last undone action"""
        if self.redo_stack:
            # Save current state to undo
            state = {
                "components": copy.deepcopy(self.components),
                "wires": copy.deepcopy(self.wires),
                "node_to_component": copy.deepcopy(self.node_to_component),
            }
            self.undo_stack.append(state)
            
            # Restore from redo stack
            next_state = self.redo_stack.pop()
            self.components = next_state["components"]
            self.wires = next_state["wires"]
            self.node_to_component = next_state["node_to_component"]
            self.selected_component = None
            self.selected_components = []
            
            self.undo_redo_changed.emit(len(self.undo_stack) > 0, len(self.redo_stack) > 0)
            self.circuit_changed.emit()
            self.update()
    
    # ============== CLIPBOARD OPERATIONS ==============
    
    def cut(self, comp_id: str):
        """Cut component to clipboard"""
        if comp_id in self.components:
            self.copy(comp_id)
            self.save_state()
            self._on_delete(comp_id)
    
    def copy(self, comp_id: str):
        """Copy component to clipboard"""
        if comp_id in self.components:
            # Get component and its nodes
            comp = self.components[comp_id]
            comp_nodes = [nid for nid, cid in self.node_to_component.items() if cid == comp_id]
            nodes_data = {nid: self.nodes[nid] for nid in comp_nodes if nid in self.nodes}
            
            self.clipboard = {
                "components": [copy.deepcopy(comp)],
                "nodes": [copy.deepcopy(n) for n in nodes_data.values()],
                "wires": [],
            }
            self.clipboard_changed.emit(True)
    
    def paste(self, offset_x: float = 30, offset_y: float = 30):
        """Paste component from clipboard"""
        if not self.clipboard.get("components"):
            return
        
        self.save_state()
        
        # Paste with offset to prevent exact overlap
        for comp in self.clipboard["components"]:
            new_comp_id = f"comp_{len(self.components)}"
            new_comp = copy.deepcopy(comp)
            new_comp.comp_id = new_comp_id
            new_comp.x += offset_x
            new_comp.y += offset_y
            new_comp.selected = False
            
            self.components[new_comp_id] = new_comp
            self._add_component_nodes(new_comp_id)
        
        self.circuit_changed.emit()
        self.update()
    
    def select_all(self):
        """Select all components on canvas"""
        self.selected_components = list(self.components.keys())
        for comp_id in self.selected_components:
            self.components[comp_id].selected = True
        self.update()
    
    def clear_selection(self):
        """Clear all selections"""
        for comp_id in self.selected_components:
            if comp_id in self.components:
                self.components[comp_id].selected = False
        self.selected_component = None
        self.selected_components = []
        self.update()
    
    def duplicate_selected(self):
        """Duplicate selected component"""
        if self.selected_component and self.selected_component in self.components:
            self.save_state()
            self.paste(offset_x=50, offset_y=50)
    
    def _auto_fix_ground_components(self):
        """Auto-fix ground components that have wrong number of ports"""
        for comp_id, comp in self.components.items():
            if "ground" in comp.name.lower():
                # Count current nodes for this component
                current_node_count = sum(1 for nid, cid in self.node_to_component.items() if cid == comp_id)
                
                # Ground should have exactly 1 node
                if current_node_count != 1:
                    # Fix by re-adding nodes
                    self._add_component_nodes(comp_id)



