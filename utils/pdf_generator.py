"""
Generador de PDF usando las utilidades existentes
"""
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, NextPageTemplate, PageTemplate, Frame, BaseDocTemplate

from .pdf_styles import setup_pdf_styles
from .pdf_tables import create_summary_table, create_test_details_table


def generate_pdf_report(modules, filename='test_report.pdf'):
    """
    Genera el PDF completo con todos los módulos
    
    Args:
        modules: Dict con módulos y sus tests organizados
        filename: Nombre del archivo PDF a generar
    """
    # Configurar estilos
    styles = setup_pdf_styles()
    
    # Crear templates para diferentes orientaciones
    # Template para páginas verticales (resumen)
    portrait_frame = Frame(72, 18, A4[0] - 144, A4[1] - 90, id='portrait')
    portrait_template = PageTemplate(id='portrait', frames=[portrait_frame])
    
    # Template para páginas horizontales (detalles)
    landscape_frame = Frame(50, 50, landscape(A4)[0] - 100, landscape(A4)[1] - 100, id='landscape')
    landscape_template = PageTemplate(id='landscape', frames=[landscape_frame], pagesize=landscape(A4))
    
    # Crear documento con múltiples templates
    doc = BaseDocTemplate(filename, pageTemplates=[portrait_template, landscape_template])
    
    story = []
    
    # === PÁGINA 1: RESUMEN GENERAL ===
    story.extend(_create_header_section(styles))
    story.extend(_create_summary_section(modules, styles))
    
    # === PÁGINAS DETALLADAS: UNA POR MÓDULO ===
    story.extend(_create_details_sections(modules, styles))
    
    # Construir el PDF
    doc.build(story)
    print(f"📄 Reporte PDF generado: {filename}")


def _create_header_section(styles):
    """Crea la sección de encabezado del PDF"""
    elements = []
    
    # Título principal
    title = Paragraph('Reporte de Tests - NutriPAE', styles['CustomTitle'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Información general
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y %H:%M:%S")
    
    info_text = f"""
    <b>Fecha de Ejecución:</b> {date_str}<br/>
    <b>Proyecto:</b> NutriPAE - Sistema de Gestión Nutricional<br/>
    <b>Versión:</b> 1.0<br/>
    <b>Entorno:</b> Testing<br/>
    <b>Servicios:</b> Autenticación, Compras, Menús<br/>
    <b>Metadata:</b> Extraída dinámicamente del código fuente
    """
    
    info_para = Paragraph(info_text, styles['CustomNormal'])
    elements.append(info_para)
    elements.append(Spacer(1, 30))
    
    return elements


def _create_summary_section(modules, styles):
    """Crea la sección de resumen ejecutivo"""
    elements = []
    
    # Título del resumen
    elements.append(Paragraph('Resumen Ejecutivo - Todos los Servicios', styles['ModuleTitle']))
    elements.append(Spacer(1, 15))
    
    # Tabla resumen usando la función existente
    summary_table = create_summary_table(modules, styles)
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    return elements


def _create_details_sections(modules, styles):
    """Crea las secciones detalladas para cada módulo"""
    elements = []
    
    # Cambiar a orientación horizontal para los detalles
    elements.append(NextPageTemplate('landscape'))
    elements.append(PageBreak())
    
    # Título para la sección de detalles
    title_details = Paragraph('Detalles por Módulo', styles['CustomTitle'])
    elements.append(title_details)
    elements.append(Spacer(1, 20))
    
    # Módulos ordenados alfabéticamente (ya vienen ordenados del test_runner)
    for i, (module_name, tests) in enumerate(modules.items()):
        if i > 0:  # Salto de página antes de cada módulo (excepto el primero)
            elements.append(PageBreak())
        
        # Título del módulo
        module_title = Paragraph(f'Módulo: {module_name}', styles['ModuleTitle'])
        elements.append(module_title)
        elements.append(Spacer(1, 15))
        
        # Estadísticas del módulo
        passed = sum(1 for test in tests if test['outcome'] == 'passed')
        failed = len(tests) - passed
        success_rate = (passed / len(tests)) * 100 if tests else 0
        
        stats_text = f"""
        <b>Tests Totales:</b> {len(tests)} | 
        <b>Pasaron:</b> {passed} | 
        <b>Fallaron:</b> {failed} | 
        <b>Porcentaje de Éxito:</b> {success_rate:.1f}%
        """
        
        stats_para = Paragraph(stats_text, styles['Summary'])
        elements.append(stats_para)
        elements.append(Spacer(1, 15))
        
        # Tabla de tests del módulo usando la función existente
        module_table = create_test_details_table(tests, styles)
        elements.append(module_table)
        elements.append(Spacer(1, 20))
    
    return elements 