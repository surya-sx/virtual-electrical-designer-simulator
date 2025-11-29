"""
Report Generator - build professional reports and export to multiple formats
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import csv
from dataclasses import dataclass, asdict


@dataclass
class ReportMetadata:
    """Report metadata"""
    report_type: str
    timestamp: str
    project_name: str
    circuit_name: str
    total_components: int = 0
    total_wires: int = 0


class ReportGenerator:
    """Generate professional reports with multiple export formats"""
    
    def __init__(self, project_name: str = "Unknown", circuit_name: str = "Untitled"):
        self.timestamp = datetime.now()
        self.project_name = project_name
        self.circuit_name = circuit_name
        self.metadata = ReportMetadata(
            report_type="general",
            timestamp=self.timestamp.isoformat(),
            project_name=project_name,
            circuit_name=circuit_name,
        )
        
    def build_summary(self, components: Dict, wires: Dict, properties: Optional[Dict] = None) -> str:
        """Build circuit summary report"""
        summary = []
        summary.append("=" * 60)
        summary.append("CIRCUIT SUMMARY REPORT")
        summary.append("=" * 60)
        summary.append("")
        summary.append(f"Project:          {self.project_name}")
        summary.append(f"Circuit:          {self.circuit_name}")
        summary.append(f"Generated:        {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        summary.append("CIRCUIT STATISTICS")
        summary.append("-" * 60)
        summary.append(f"Total Components: {len(components)}")
        summary.append(f"Total Connections: {len(wires)}")
        summary.append("")
        
        # Component breakdown
        if components:
            type_count = {}
            for comp in components.values():
                comp_type = comp.get("comp_type", "Unknown")
                type_count[comp_type] = type_count.get(comp_type, 0) + 1
            
            summary.append("Component Breakdown:")
            for comp_type, count in sorted(type_count.items()):
                summary.append(f"  {comp_type:20} {count:3} units")
        
        summary.append("")
        summary.append("=" * 60)
        
        return "\n".join(summary)
    
    def build_bom(self, components: Dict) -> str:
        """Build bill of materials report"""
        bom = []
        bom.append("=" * 80)
        bom.append("BILL OF MATERIALS (BOM)")
        bom.append("=" * 80)
        bom.append("")
        bom.append(f"Project:  {self.project_name}")
        bom.append(f"Circuit:  {self.circuit_name}")
        bom.append(f"Date:     {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        bom.append("")
        
        # Table header
        bom.append(f"{'Ref Des':<10} {'Type':<15} {'Value':<15} {'Quantity':<10} {'Notes':<20}")
        bom.append("-" * 80)
        
        # Compile BOM
        bom_items = {}
        for comp_id, component in components.items():
            comp_type = component.get("comp_type", "Unknown")
            comp_value = component.get("value", "-")
            comp_name = component.get("name", comp_id)
            
            key = (comp_type, comp_value)
            if key not in bom_items:
                bom_items[key] = {"names": [], "value": comp_value, "type": comp_type, "count": 0}
            
            bom_items[key]["names"].append(comp_name)
            bom_items[key]["count"] += 1
        
        # Display BOM entries
        for (comp_type, comp_value), item in sorted(bom_items.items()):
            names = ", ".join(item["names"][:3])  # Show first 3 names
            if len(item["names"]) > 3:
                names += f", +{len(item['names']) - 3} more"
            
            bom.append(f"{names:<10} {comp_type:<15} {comp_value:<15} {item['count']:<10} {'':20}")
        
        bom.append("")
        bom.append("=" * 80)
        
        return "\n".join(bom)
    
    def build_simulation_results(self, sim_type: str, sim_data: Dict) -> str:
        """Build simulation results report"""
        results = []
        results.append("=" * 60)
        results.append("SIMULATION RESULTS REPORT")
        results.append("=" * 60)
        results.append("")
        results.append(f"Project:           {self.project_name}")
        results.append(f"Circuit:           {self.circuit_name}")
        results.append(f"Simulation Type:   {sim_type}")
        results.append(f"Generated:         {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        results.append("")
        
        results.append("SIMULATION DATA")
        results.append("-" * 60)
        
        if sim_type == "dc":
            results.append("DC Operating Point Analysis")
            results.append("Node Voltages:")
            for node_id, voltage in sim_data.get("node_voltages", {}).items():
                results.append(f"  {node_id:15}: {voltage:12.6f} V")
        
        elif sim_type == "ac":
            results.append("AC Frequency Response Analysis")
            results.append(f"Frequency Points: {len(sim_data.get('frequencies', []))}")
            results.append(f"Frequency Range:  {min(sim_data.get('frequencies', [1]))} Hz - {max(sim_data.get('frequencies', [1e6]))} Hz")
        
        elif sim_type == "transient":
            results.append("Transient Time-Domain Analysis")
            results.append(f"Time Points:      {len(sim_data.get('time_points', []))}")
            results.append(f"Time Span:        {min(sim_data.get('time_points', [0]))} - {max(sim_data.get('time_points', [1]))} seconds")
        
        elif sim_type == "monte_carlo":
            results.append("Monte Carlo Statistical Analysis")
            results.append(f"Samples:          {sim_data.get('sample_count', 100)}")
            results.append(f"Mean:             {sim_data.get('mean', 0):.6f}")
            results.append(f"Std Dev:          {sim_data.get('std', 0):.6f}")
        
        results.append("")
        results.append("=" * 60)
        
        return "\n".join(results)
    
    def export_html(self, summary: str, bom: str, results: str, filename: str) -> bool:
        """Export complete report to HTML"""
        try:
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Circuit Report - {self.circuit_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
        h2 {{ color: #0066cc; margin-top: 30px; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #0066cc; color: white; }}
        .metadata {{ background-color: #e8f4f8; padding: 10px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>Circuit Report: {self.circuit_name}</h1>
    <div class="metadata">
        <strong>Project:</strong> {self.project_name}<br>
        <strong>Generated:</strong> {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}<br>
    </div>
    
    <h2>Circuit Summary</h2>
    <pre>{summary}</pre>
    
    <h2>Bill of Materials</h2>
    <pre>{bom}</pre>
    
    <h2>Simulation Results</h2>
    <pre>{results}</pre>
    
    <hr>
    <p><small>Generated by Virtual Electrical Designer & Simulator</small></p>
</body>
</html>"""
            
            with open(filename, 'w') as f:
                f.write(html)
            return True
        except Exception as e:
            print(f"Error exporting HTML: {e}")
            return False
    
    def export_pdf(self, summary: str, bom: str, results: str, filename: str) -> bool:
        """Export complete report to PDF"""
        try:
            # Try to use reportlab if available, otherwise create simple text PDF
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.lib import colors
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                
                doc = SimpleDocTemplate(filename, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#0066cc'),
                    spaceAfter=30,
                )
                elements.append(Paragraph(f"Circuit Report: {self.circuit_name}", title_style))
                elements.append(Spacer(1, 12))
                
                # Content sections
                elements.append(Paragraph(f"<b>Summary Report</b>", styles['Heading2']))
                elements.append(Paragraph(f"<pre>{summary}</pre>", styles['Normal']))
                elements.append(Spacer(1, 12))
                
                elements.append(Paragraph(f"<b>Bill of Materials</b>", styles['Heading2']))
                elements.append(Paragraph(f"<pre>{bom}</pre>", styles['Normal']))
                elements.append(Spacer(1, 12))
                
                doc.build(elements)
                return True
            
            except ImportError:
                # Fallback: Create simple text-based PDF
                with open(filename.replace('.pdf', '.txt'), 'w') as f:
                    f.write(f"CIRCUIT REPORT: {self.circuit_name}\n\n")
                    f.write(summary)
                    f.write("\n\n")
                    f.write(bom)
                    f.write("\n\n")
                    f.write(results)
                return True
        
        except Exception as e:
            print(f"Error exporting PDF: {e}")
            return False
    
    def export_json(self, data: Dict, filename: str) -> bool:
        """Export data to JSON format"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return False
    
    def export_csv(self, items: List[Dict], filename: str) -> bool:
        """Export BOM items to CSV"""
        try:
            if not items:
                return False
            
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=items[0].keys())
                writer.writeheader()
                writer.writerows(items)
            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False
