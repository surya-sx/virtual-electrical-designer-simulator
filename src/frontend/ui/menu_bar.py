"""
Menu bar for Virtual Electrical Designer & Simulator
"""
from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction, QKeySequence


class MenuBar(QMenuBar):
    """Application menu bar with all menus"""
    
    def __init__(self):
        super().__init__()
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_simulation_menu()
        self._create_tools_menu()
        self._create_window_menu()
        self._create_help_menu()
        
    def _create_file_menu(self):
        """File menu"""
        file_menu = self.addMenu("&File")
        
        actions = [
            ("&New", QKeySequence.New),
            ("&Open", QKeySequence.Open),
            ("&Save", QKeySequence.Save),
            ("Save &As", QKeySequence.SaveAs),
            ("Recent", None),
            (None, None),  # Separator
            ("&Import", None),
            ("&Export", None),
            ("&Preferences", QKeySequence.Preferences),
            (None, None),  # Separator
            ("E&xit", QKeySequence.Quit),
        ]
        
        for action_name, shortcut in actions:
            if action_name is None:
                file_menu.addSeparator()
            else:
                action = QAction(action_name, self)
                if shortcut:
                    action.setShortcut(shortcut)
                file_menu.addAction(action)
                
    def _create_edit_menu(self):
        """Edit menu"""
        edit_menu = self.addMenu("&Edit")
        
        actions = [
            ("&Undo", QKeySequence.Undo),
            ("&Redo", QKeySequence.Redo),
            (None, None),
            ("Cu&t", QKeySequence.Cut),
            ("&Copy", QKeySequence.Copy),
            ("&Paste", QKeySequence.Paste),
            ("&Duplicate", QKeySequence("Ctrl+D")),
            ("&Delete", QKeySequence.Delete),
            (None, None),
            ("Select &All", QKeySequence.SelectAll),
            (None, None),
            ("&Group", QKeySequence("Ctrl+G")),
            ("&Ungroup", QKeySequence("Ctrl+Shift+G")),
            ("&Align", None),
            ("Snap to &Grid", QKeySequence("Ctrl+Shift+S")),
        ]
        
        for action_name, shortcut in actions:
            if action_name is None:
                edit_menu.addSeparator()
            else:
                action = QAction(action_name, self)
                if shortcut:
                    action.setShortcut(shortcut)
                edit_menu.addAction(action)
                
    def _create_view_menu(self):
        """View menu"""
        view_menu = self.addMenu("&View")
        
        actions = [
            ("Zoom &In", QKeySequence.ZoomIn),
            ("Zoom &Out", QKeySequence.ZoomOut),
            ("&Reset Zoom", QKeySequence("Ctrl+0")),
            (None, None),
            ("Toggle &Grid", QKeySequence("Ctrl+'")),
            ("Toggle &Panels", QKeySequence("Ctrl+Alt+P")),
            ("Layout &Presets", None),
        ]
        
        for action_name, shortcut in actions:
            if action_name is None:
                view_menu.addSeparator()
            else:
                action = QAction(action_name, self)
                if shortcut:
                    action.setShortcut(shortcut)
                view_menu.addAction(action)
                
    def _create_simulation_menu(self):
        """Simulation menu"""
        sim_menu = self.addMenu("&Simulation")
        
        actions = [
            ("&Run", QKeySequence("Ctrl+Enter")),
            ("&Pause", QKeySequence("Ctrl+Shift+P")),
            ("S&top", QKeySequence("Ctrl+Shift+Q")),
            ("Ste&p", QKeySequence("Ctrl+Shift+S")),
            (None, None),
            ("Manage &Profiles", None),
        ]
        
        for action_name, shortcut in actions:
            if action_name is None:
                sim_menu.addSeparator()
            else:
                action = QAction(action_name, self)
                if shortcut:
                    action.setShortcut(shortcut)
                sim_menu.addAction(action)
                
    def _create_tools_menu(self):
        """Tools menu"""
        tools_menu = self.addMenu("&Tools")
        
        actions = [
            "Transformer Designer",
            "Cable Sizing",
            "Fault Calculator",
            "PF Correction",
            "Battery Tool",
            "Component Library Manager",
            "Script Manager",
        ]
        
        for action_name in actions:
            action = QAction(action_name, self)
            tools_menu.addAction(action)
            
    def _create_window_menu(self):
        """Window menu"""
        window_menu = self.addMenu("&Window")
        
        actions = [
            ("&New Window", None),
            ("&Reset Layout", None),
            (None, None),
            ("Save Layout &Preset", None),
            ("&Load Layout Preset", None),
        ]
        
        for action_name, shortcut in actions:
            if action_name is None:
                window_menu.addSeparator()
            else:
                action = QAction(action_name, self)
                if shortcut:
                    action.setShortcut(shortcut)
                window_menu.addAction(action)
                
    def _create_help_menu(self):
        """Help menu"""
        help_menu = self.addMenu("&Help")
        
        actions = [
            ("&Documentation", QKeySequence.HelpContents),
            ("&Keyboard Shortcuts", QKeySequence("Ctrl+?")),
            (None, None),
            ("&About", None),
        ]
        
        for action_name, shortcut in actions:
            if action_name is None:
                help_menu.addSeparator()
            else:
                action = QAction(action_name, self)
                if shortcut:
                    action.setShortcut(shortcut)
                help_menu.addAction(action)
