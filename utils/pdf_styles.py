"""
Configuración de estilos para el PDF
"""
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def setup_pdf_styles():
    """Configura y retorna todos los estilos personalizados para el PDF"""
    styles = getSampleStyleSheet()
    
    # Título principal
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=20,
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Subtítulo de módulo
    styles.add(ParagraphStyle(
        name='ModuleTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkgreen,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    ))
    
    # Texto normal
    styles.add(ParagraphStyle(
        name='CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        fontName='Helvetica'
    ))
    
    # Resumen
    styles.add(ParagraphStyle(
        name='Summary',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        textColor=colors.darkblue,
        alignment=TA_CENTER
    ))
    
    # Estilo para texto en tablas
    styles.add(ParagraphStyle(
        name='TableText',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        alignment=TA_CENTER,
        leading=11
    ))
    
    return styles


def get_table_colors():
    """Retorna configuración de colores para tablas"""
    return {
        'header_bg': colors.darkblue,
        'header_text': colors.whitesmoke,
        'content_bg': colors.beige,
        'row_bg_1': colors.white,
        'row_bg_2': colors.lightgrey,
        'summary_header_bg': colors.darkgreen,
        'summary_content_bg': colors.lightblue,
        'summary_total_bg': colors.yellow,
        'grid': colors.black
    } 