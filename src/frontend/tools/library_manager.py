"""Library Manager Tool - Separate Window"""
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout, QFileDialog,
    QWidget, QToolBar, QStatusBar, QScrollArea
)
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont
from pathlib import Path
import json


class LibraryManagerWindow(QMainWindow):
    """Tool for managing component libraries"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Library Manager")
        self.setGeometry(100, 100, 900, 750)
        self.setMinimumSize(900, 750)
        
        self.libraries_path = Path("data/libraries")
        
        self._setup_ui()
        self._load_libraries()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Create scrollable main widget
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        scroll.setWidget(main_widget)
        self.setCentralWidget(scroll)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Toolbar
        toolbar = QToolBar("Library Manager Toolbar")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        refresh_btn = toolbar.addAction("Refresh")
        refresh_btn.triggered.connect(self._load_libraries)
        
        import_btn = toolbar.addAction("Import")
        import_btn.triggered.connect(self._import_library)
        
        export_btn = toolbar.addAction("Export")
        export_btn.triggered.connect(self._export_library)
        
        delete_btn = toolbar.addAction("Delete")
        delete_btn.triggered.connect(self._delete_library)
        
        # Title
        title = QLabel("Component Library Manager")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Libraries Table
        table_group = QGroupBox("Available Libraries")
        table_layout = QVBoxLayout()
        
        self.libraries_table = QTableWidget()
        self.libraries_table.setColumnCount(4)
        self.libraries_table.setHorizontalHeaderLabels(["Library Name", "Components", "Size (KB)", "Last Modified"])
        self.libraries_table.setColumnWidth(0, 200)
        self.libraries_table.setColumnWidth(1, 100)
        self.libraries_table.setColumnWidth(2, 100)
        self.libraries_table.setColumnWidth(3, 150)
        
        table_layout.addWidget(self.libraries_table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Info Group
        info_group = QGroupBox("Library Details")
        info_layout = QFormLayout()
        
        self.selected_lib = QLineEdit()
        self.selected_lib.setReadOnly(True)
        info_layout.addRow("Selected Library:", self.selected_lib)
        
        self.lib_components = QLineEdit()
        self.lib_components.setReadOnly(True)
        info_layout.addRow("Total Components:", self.lib_components)
        
        self.lib_size = QLineEdit()
        self.lib_size.setReadOnly(True)
        info_layout.addRow("Library Size:", self.lib_size)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        main_layout.addStretch()
        
        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
    
    def _load_libraries(self):
        """Load and display available libraries"""
        self.libraries_table.setRowCount(0)
        
        if not self.libraries_path.exists():
            return
        
        row = 0
        for lib_file in sorted(self.libraries_path.glob("*.json")):
            try:
                # Get file info
                size_kb = lib_file.stat().st_size / 1024
                
                # Load library to count components
                with open(lib_file, 'r') as f:
                    lib_data = json.load(f)
                
                component_count = len(lib_data.get("components", []))
                
                self.libraries_table.insertRow(row)
                self.libraries_table.setItem(row, 0, QTableWidgetItem(lib_file.stem))
                self.libraries_table.setItem(row, 1, QTableWidgetItem(str(component_count)))
                self.libraries_table.setItem(row, 2, QTableWidgetItem(f"{size_kb:.1f}"))
                self.libraries_table.setItem(row, 3, QTableWidgetItem(lib_file.stat().st_mtime.__str__()[:19]))
                
                row += 1
            except Exception as e:
                print(f"Error loading {lib_file}: {e}")
    
    def _import_library(self):
        """Import a new library"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("JSON Libraries (*.json)")
        
        if file_dialog.exec():
            source_file = Path(file_dialog.selectedFiles()[0])
            dest_file = self.libraries_path / source_file.name
            
            try:
                import shutil
                shutil.copy(source_file, dest_file)
                self._load_libraries()
            except Exception as e:
                print(f"Import error: {e}")
    
    def _export_library(self):
        """Export selected library"""
        selected_row = self.libraries_table.currentRow()
        if selected_row < 0:
            return
        
        lib_name = self.libraries_table.item(selected_row, 0).text()
        
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter("JSON Libraries (*.json)")
        file_dialog.setDefaultSuffix("json")
        
        if file_dialog.exec():
            dest_file = Path(file_dialog.selectedFiles()[0])
            
            try:
                import shutil
                source_file = self.libraries_path / f"{lib_name}.json"
                shutil.copy(source_file, dest_file)
            except Exception as e:
                print(f"Export error: {e}")
    
    def _delete_library(self):
        """Delete selected library"""
        selected_row = self.libraries_table.currentRow()
        if selected_row < 0:
            return
        
        lib_name = self.libraries_table.item(selected_row, 0).text()
        lib_file = self.libraries_path / f"{lib_name}.json"
        
        try:
            lib_file.unlink()
            self._load_libraries()
        except Exception as e:
            print(f"Delete error: {e}")
