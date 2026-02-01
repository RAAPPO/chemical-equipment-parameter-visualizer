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

from .models import Dataset

# Initialize logger
logger = logging.getLogger(__name__)

def generate_dataset_pdf(dataset_id):
    """
    Generate a comprehensive PDF report for a dataset.
    
    Args:
        dataset_id: UUID of the dataset
        
    Returns:
        BytesIO: PDF file buffer
        
    Raises:
        ValueError: If dataset not found
        Exception: If PDF generation fails
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
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Equipment Type Distribution
        elements.append(Paragraph("Equipment Type Distribution", heading_style))
        
        type_counts = {}
        for eq in equipment_list:
            type_counts[eq.equipment_type] = type_counts.get(eq.equipment_type, 0) + 1
        
        dist_data = [['Equipment Type', 'Count', 'Percentage']]
        for eq_type, count in sorted(type_counts.items()):
            percentage = (count / dataset.total_equipment) * 100
            dist_data.append([eq_type, str(count), f"{percentage:.1f}%"])
        
        dist_table = Table(dist_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(dist_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Outlier Detection Section
        outliers = equipment_list.filter(
            is_pressure_outlier=True
        ) | equipment_list.filter(
            is_temperature_outlier=True
        )
        
        elements.append(Paragraph("Outlier Detection (Z-score > 2)", heading_style))
        
        if outliers.exists():
            outlier_data = [['Equipment', 'Type', 'Pressure Outlier', 'Temp Outlier']]
            for eq in outliers.distinct():
                outlier_data.append([
                    eq.equipment_name,
                    eq.equipment_type,
                    '⚠️ YES' if eq.is_pressure_outlier else 'No',
                    '⚠️ YES' if eq.is_temperature_outlier else 'No',
                ])
            
            outlier_table = Table(outlier_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
            outlier_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightpink),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(outlier_table)
        else:
            elements.append(Paragraph(
                "✅ No outliers detected. All equipment parameters are within normal range.",
                styles['Normal']
            ))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Detailed Equipment List (on new page)
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Equipment List", heading_style))
        
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