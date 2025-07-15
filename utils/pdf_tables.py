"""
Generación de tablas para el PDF
"""
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph
from .pdf_styles import get_table_colors


def create_test_details_table(tests, styles):
    """
    Crea una tabla detallada con los resultados de los tests
    
    Args:
        tests: Lista de tests con su información
        styles: Estilos del PDF
        
    Returns:
        Table: Tabla configurada para el PDF
    """
    colors = get_table_colors()
    
    # Encabezados de la tabla
    headers = [
        Paragraph('<b>ID</b>', styles['TableText']),
        Paragraph('<b>Test</b>', styles['TableText']),
        Paragraph('<b>Descripción</b>', styles['TableText']),
        Paragraph('<b>Resultado Esperado</b>', styles['TableText']),
        Paragraph('<b>Resultado Obtenido</b>', styles['TableText']),
        Paragraph('<b>Estado</b>', styles['TableText']),
        Paragraph('<b>Duración(s)</b>', styles['TableText'])
    ]
    
    # Datos de la tabla
    data = [headers]
    
    for test in tests:
        status_color = '<font color="green">✓ PASS</font>' if test['outcome'] == 'passed' else '<font color="red">✗ FAIL</font>'
        
        data.append([
            Paragraph(test.get('test_id', 'N/A'), styles['TableText']),
            Paragraph(test['name'], styles['TableText']),
            Paragraph(test['description'], styles['TableText']),
            Paragraph(test['expected_result'], styles['TableText']),
            Paragraph(test['actual_result'], styles['TableText']),
            Paragraph(status_color, styles['TableText']),
            Paragraph(str(test['duration']), styles['TableText'])
        ])
    
    # Crear tabla con anchos apropiados para orientación horizontal
    table = Table(data, colWidths=[
        0.6*inch,  # ID
        1.5*inch,  # Test name
        2.8*inch,  # Description
        2.0*inch,  # Expected result
        2.0*inch,  # Actual result
        0.8*inch,  # Status
        0.6*inch   # Duration
    ])
    
    # Aplicar estilo a la tabla
    table.setStyle(TableStyle([
        # Encabezados
        ('BACKGROUND', (0, 0), (-1, 0), colors['header_bg']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors['header_text']),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Contenido
        ('BACKGROUND', (0, 1), (-1, -1), colors['content_bg']),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors['grid']),
        
        # Alternar colores de filas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors['row_bg_1'], colors['row_bg_2']]),
        
        # Padding para mejor legibilidad
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    return table


def create_summary_table(modules, styles):
    """
    Crea una tabla resumen con estadísticas por módulo
    
    Args:
        modules: Dict con módulos y sus tests
        styles: Estilos del PDF
        
    Returns:
        Table: Tabla resumen configurada
    """
    colors = get_table_colors()
    
    headers = ['Módulo', 'Tests Totales', 'Pasaron', 'Fallaron', 'Porcentaje Éxito']
    data = [headers]
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    
    # Ordenar módulos alfabéticamente
    sorted_modules = sorted(modules.items())
    
    for module_name, tests in sorted_modules:
        passed = sum(1 for test in tests if test['outcome'] == 'passed')
        failed = len(tests) - passed
        success_rate = (passed / len(tests)) * 100 if tests else 0
        
        total_tests += len(tests)
        total_passed += passed
        total_failed += failed
        
        data.append([
            module_name,
            str(len(tests)),
            str(passed),
            str(failed),
            f"{success_rate:.1f}%"
        ])
    
    # Fila de totales
    total_success_rate = (total_passed / total_tests) * 100 if total_tests else 0
    data.append([
        'TOTAL GENERAL',
        str(total_tests),
        str(total_passed),
        str(total_failed),
        f"{total_success_rate:.1f}%"
    ])
    
    # Crear tabla
    table = Table(data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
    
    # Aplicar estilo a la tabla
    table.setStyle(TableStyle([
        # Encabezados
        ('BACKGROUND', (0, 0), (-1, 0), colors['summary_header_bg']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors['header_text']),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        
        # Contenido
        ('BACKGROUND', (0, 1), (-1, -2), colors['summary_content_bg']),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors['grid']),
        
        # Fila de totales
        ('BACKGROUND', (0, -1), (-1, -1), colors['summary_total_bg']),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    return table 