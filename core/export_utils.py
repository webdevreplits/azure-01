"""
Export utilities for reports and dashboards.
Supports PDF and Excel export formats.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

class ExportUtils:
    """Utility class for exporting data to various formats."""
    
    @staticmethod
    def export_to_excel(data: Dict[str, pd.DataFrame], title: str = "Azure Report") -> bytes:
        """
        Export data to Excel format with multiple sheets.
        
        Args:
            data: Dictionary of {sheet_name: dataframe}
            title: Report title
            
        Returns:
            Excel file as bytes
        """
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, df in data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Format the worksheet
                worksheet = writer.sheets[sheet_name]
                
                # Style header row
                header_fill = PatternFill(start_color="0078D4", end_color="0078D4", fill_type="solid")
                header_font = Font(bold=True, color="FFFFFF")
                
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    def export_to_pdf(data: Dict[str, Any], title: str = "Azure Report") -> bytes:
        """
        Export data to PDF format.
        
        Args:
            data: Dictionary containing report data
            title: Report title
            
        Returns:
            PDF file as bytes
        """
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0078D4'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0078D4'),
            spaceAfter=10
        )
        
        # Title
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add sections
        for section_title, section_data in data.items():
            story.append(Paragraph(section_title, heading_style))
            
            if isinstance(section_data, pd.DataFrame):
                # Convert DataFrame to table
                table_data = [section_data.columns.tolist()] + section_data.values.tolist()
                
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0078D4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                
                story.append(table)
            
            elif isinstance(section_data, dict):
                # Display as key-value pairs
                for key, value in section_data.items():
                    story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
            
            elif isinstance(section_data, list):
                # Display as bullet points
                for item in section_data:
                    story.append(Paragraph(f"• {item}", styles['Normal']))
            
            else:
                # Display as text
                story.append(Paragraph(str(section_data), styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    def create_incident_report(incidents: List[Dict[str, Any]]) -> bytes:
        """Create a detailed incident report in PDF format."""
        # Convert incidents to DataFrame
        df_incidents = pd.DataFrame(incidents)
        
        # Summary statistics
        total_incidents = len(incidents)
        open_incidents = len([i for i in incidents if i.get('status') == 'Open'])
        resolved_incidents = len([i for i in incidents if i.get('status') == 'Resolved'])
        
        data = {
            'Summary': {
                'Total Incidents': total_incidents,
                'Open Incidents': open_incidents,
                'Resolved Incidents': resolved_incidents,
                'Resolution Rate': f"{(resolved_incidents/total_incidents*100):.1f}%" if total_incidents > 0 else "0%"
            },
            'Incident Details': df_incidents[['incident_id', 'title', 'status', 'priority', 'assignee']] if not df_incidents.empty else pd.DataFrame()
        }
        
        return ExportUtils.export_to_pdf(data, "Incident Report")
    
    @staticmethod
    def create_cost_report(cost_data: Dict[str, Any]) -> bytes:
        """Create a cost analysis report in Excel format."""
        sheets = {}
        
        # Summary sheet
        if 'total_cost' in cost_data:
            summary_data = {
                'Metric': ['Total Cost', 'Average Daily Cost', 'Period'],
                'Value': [
                    f"${cost_data.get('total_cost', 0):.2f}",
                    f"${cost_data.get('average_daily_cost', 0):.2f}",
                    f"{len(cost_data.get('dates', []))} days"
                ]
            }
            sheets['Summary'] = pd.DataFrame(summary_data)
        
        # Daily costs sheet
        if 'dates' in cost_data and 'daily_costs' in cost_data:
            daily_data = {
                'Date': cost_data['dates'],
                'Cost': [f"${c:.2f}" for c in cost_data['daily_costs']]
            }
            sheets['Daily Costs'] = pd.DataFrame(daily_data)
        
        # Cost by service sheet
        if 'cost_by_service' in cost_data:
            service_data = {
                'Service': list(cost_data['cost_by_service'].keys()),
                'Cost': [f"${c:.2f}" for c in cost_data['cost_by_service'].values()]
            }
            sheets['By Service'] = pd.DataFrame(service_data)
        
        return ExportUtils.export_to_excel(sheets, "Cost Analysis Report")
    
    @staticmethod
    def create_resource_report(resources: List[Dict[str, Any]]) -> bytes:
        """Create a resource inventory report in Excel format."""
        df_resources = pd.DataFrame(resources)
        
        sheets = {
            'All Resources': df_resources,
        }
        
        # Group by type
        if not df_resources.empty and 'type' in df_resources.columns:
            for resource_type in df_resources['type'].unique():
                type_df = df_resources[df_resources['type'] == resource_type]
                sheets[resource_type[:30]] = type_df  # Excel sheet name limit
        
        return ExportUtils.export_to_excel(sheets, "Resource Inventory Report")
