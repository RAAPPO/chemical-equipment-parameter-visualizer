import io
import logging
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)

# ADDED IMPORTS
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from .models import Dataset

# Initialize logger
logger = logging.getLogger(__name__)

# NEW FUNCTION: create_chart_image
def create_chart_image(chart_type, data, title):
    """
    Generate matplotlib chart and return as PNG BytesIO
    
    Args:
        chart_type: 'bar', 'pie', 'scatter', 'box'
        data: dict with chart data
        title: Chart title
    
    Returns:
        BytesIO: PNG image buffer
    """
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    
    if chart_type == 'bar':
        ax.bar(data['labels'], data['values'], color='#3B82F6')
        ax.set_ylabel(data.get('ylabel', 'Value'))
        
    elif chart_type == 'pie':
        ax.pie(data['values'], labels=data['labels'], autopct='%1.1f%%', 
               colors=['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'])
        
    elif chart_type == 'scatter':
        ax.scatter(data['x'], data['y'], alpha=0.6, c='#3B82F6', s=50)
        ax.set_xlabel(data.get('xlabel', 'X'))
        ax.set_ylabel(data.get('ylabel', 'Y'))
        ax.grid(True, alpha=0.3)
        
    elif chart_type == 'box':
        ax.boxplot(data['values'], labels=data['labels'])
        ax.set_ylabel(data.get('ylabel', 'Value'))
        ax.grid(True, alpha=0.3, axis='y')
    
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1E3A8A')
    plt.tight_layout()
    
    # Save to BytesIO
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
    img_buffer.seek(0)
    plt.close(fig)
    
    return img_buffer

def generate_dataset_pdf(dataset_id):
    """
    Generate a comprehensive PDF report for a dataset.
    """
    try:
        # Get dataset and equipment with prefetch to optimize DB hits
        dataset = Dataset.objects.prefetch_related('equipment').get(id=dataset_id)
        equipment_list = dataset.equipment.all()
        
        logger.info(f"Generating PDF for dataset {dataset_id} ({dataset.filename})")
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=12,
        )
        
        # Title
        title = Paragraph("Chemical Equipment Analysis Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Report metadata
        metadata_style = styles['Normal']
        metadata = [
            f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
            f"<b>Dataset:</b> {dataset.filename}",
            f"<b>Upload Date:</b> {dataset.uploaded_at.strftime('%B %d, %Y at %H:%M')}",
            f"<b>Total Equipment:</b> {dataset.total_equipment}",
        ]
        
        for line in metadata:
            elements.append(Paragraph(line, metadata_style))
            elements.append(Spacer(1, 0.1 * inch))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Summary Statistics Section
        elements.append(Paragraph("Summary Statistics", heading_style))
        
        summary_data = [
            ['Parameter', 'Average Value', 'Unit'],
            ['Flowrate', f"{dataset.avg_flowrate:.2f}", 'units/hr'],
            ['Pressure', f"{dataset.avg_pressure:.2f}", 'bar'],
            ['Temperature', f"{dataset.avg_temperature:.2f}", '°C'],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5 * inch, 2 * inch, 1.5 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        # ENHANCEMENTS START HERE
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # ============ NEW: EQUIPMENT TYPE DISTRIBUTION CHART ============
        elements.append(Paragraph("Equipment Type Distribution", heading_style))
        
        # Get type distribution
        type_dist = {}
        for eq in equipment_list:
            eq_type = eq.equipment_type
            type_dist[eq_type] = type_dist.get(eq_type, 0) + 1
        
        if type_dist:
            pie_data = {
                'labels': list(type_dist.keys()),
                'values': list(type_dist.values())
            }
            pie_chart = create_chart_image('pie', pie_data, 'Equipment Types')
            elements.append(Image(pie_chart, width=4*inch, height=3*inch))
            elements.append(Spacer(1, 0.3 * inch))
        
        # ============ NEW: PARAMETER COMPARISON BAR CHART ============
        elements.append(Paragraph("Average Parameters Comparison", heading_style))
        
        bar_data = {
            'labels': ['Flowrate', 'Pressure', 'Temperature'],
            'values': [dataset.avg_flowrate, dataset.avg_pressure, dataset.avg_temperature],
            'ylabel': 'Average Value'
        }
        bar_chart = create_chart_image('bar', bar_data, 'Average Parameters')
        elements.append(Image(bar_chart, width=5*inch, height=3*inch))
        elements.append(Spacer(1, 0.3 * inch))
        
        # ============ NEW: PRESSURE VS TEMPERATURE SCATTER PLOT ============
        elements.append(Paragraph("Pressure-Temperature Correlation", heading_style))
        
        pressures = [eq.pressure for eq in equipment_list]
        temperatures = [eq.temperature for eq in equipment_list]
        
        scatter_data = {
            'x': pressures,
            'y': temperatures,
            'xlabel': 'Pressure (bar)',
            'ylabel': 'Temperature (°C)'
        }
        scatter_chart = create_chart_image('scatter', scatter_data, 'Pressure vs Temperature')
        elements.append(Image(scatter_chart, width=5*inch, height=3*inch))
        elements.append(Spacer(1, 0.3 * inch))
        
        # ============ NEW: OUTLIER ANALYSIS SECTION ============
        outliers = [eq for eq in equipment_list if eq.is_pressure_outlier or eq.is_temperature_outlier]
        
        if outliers:
            elements.append(Paragraph("⚠️ Outlier Analysis", heading_style))
            
            outlier_text = f"Found {len(outliers)} equipment with abnormal readings:"
            elements.append(Paragraph(outlier_text, styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))
            
            outlier_data = [['Equipment', 'Type', 'Pressure', 'Temperature', 'Status']]
            for eq in outliers[:10]:  # Limit to 10
                status = []
                if eq.is_pressure_outlier:
                    status.append('P-Outlier')
                if eq.is_temperature_outlier:
                    status.append('T-Outlier')
                
                outlier_data.append([
                    eq.equipment_name,
                    eq.equipment_type,
                    f"{eq.pressure:.2f}",
                    f"{eq.temperature:.2f}",
                    ', '.join(status)
                ])
            
            outlier_table = Table(outlier_data, colWidths=[1.5*inch, 1.2*inch, 0.9*inch, 1*inch, 1.4*inch])
            outlier_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EF4444')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FEE2E2')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DC2626'))
            ]))
            elements.append(outlier_table)
            elements.append(Spacer(1, 0.3 * inch))
        else:
            elements.append(Paragraph("✅ No outliers detected.", styles['Normal']))
            elements.append(Spacer(1, 0.3 * inch))

        # ============ CONTINUE WITH EXISTING EQUIPMENT TABLE ============
        elements.append(PageBreak())
        elements.append(Paragraph("Complete Equipment Data", heading_style))
        
        equipment_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temp']]
        for eq in equipment_list:
            equipment_data.append([
                eq.equipment_name,
                eq.equipment_type,
                f"{eq.flowrate:.1f}",
                f"{eq.pressure:.1f}",
                f"{eq.temperature:.1f}",
            ])
        
        # Split into multiple tables if too many rows
        max_rows_per_page = 30
        for i in range(0, len(equipment_data), max_rows_per_page):
            chunk = equipment_data[i:i + max_rows_per_page]
            if i > 0:
                chunk.insert(0, equipment_data[0])  # Add header to each page
            
            eq_table = Table(chunk, colWidths=[2 * inch, 1.3 * inch, 1 * inch, 1 * inch, 1 * inch])
            eq_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            elements.append(eq_table)
            
            if i + max_rows_per_page < len(equipment_data):
                elements.append(PageBreak())
        
        # Footer
        elements.append(Spacer(1, 0.5 * inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )
        elements.append(Paragraph(
            "Generated by Chemical Equipment Parameter Visualizer | credits @ ADITYA V J ",
            footer_style
        ))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF from buffer
        buffer.seek(0)
        
        logger.info(f"PDF generated successfully for dataset {dataset_id}")
        return buffer

    except Dataset.DoesNotExist:
        logger.error(f"Dataset {dataset_id} not found for PDF generation")
        raise ValueError(f"Dataset {dataset_id} not found")
    except Exception as e:
        logger.error(f"PDF generation failed for dataset {dataset_id}: {e}", exc_info=True)
        raise