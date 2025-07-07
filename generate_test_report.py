#!/usr/bin/env python3
"""
Generador de reportes PDF para los tests de NutriPAE
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, NextPageTemplate, PageTemplate, Frame, BaseDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class TestReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.test_results = {}
        
    def setup_custom_styles(self):
        """Configura estilos personalizados para el PDF"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo de módulo
        self.styles.add(ParagraphStyle(
            name='ModuleTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Resumen
        self.styles.add(ParagraphStyle(
            name='Summary',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            textColor=colors.darkblue,
            alignment=TA_CENTER
        ))
        
        # Estilo para texto en tablas
        self.styles.add(ParagraphStyle(
            name='TableText',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            alignment=TA_CENTER,
            leading=11
        ))

    def run_tests_and_capture_results(self):
        """Ejecuta los tests y captura los resultados en formato JSON"""
        print("Ejecutando tests...")
        
        # Ejecutar tests con reporte JSON
        result = subprocess.run([
            'poetry', 'run', 'pytest', 
            'tests/auth/auth-test.py',  # Especificar el archivo de test directamente
            '--json-report', 
            '--json-report-file=test_results.json',
            '-v'
        ], capture_output=True, text=True)
        
        print("Salida de pytest:")
        print(result.stdout)
        if result.stderr:
            print("Errores:")
            print(result.stderr)
        
        # Cargar resultados JSON
        try:
            with open('test_results.json', 'r') as f:
                self.test_results = json.load(f)
        except FileNotFoundError:
            print("Error: No se pudo generar el archivo de resultados JSON")
            sys.exit(1)
            
        return result.returncode == 0

    def parse_test_info(self, test):
        """Extrae información detallada de un test"""
        # Extraer nombre del test
        test_name = test.get('nodeid', '').split('::')[-1] if '::' in test.get('nodeid', '') else test.get('nodeid', '')
        
        # Extraer módulo
        module_path = test.get('nodeid', '').split('::')[0] if '::' in test.get('nodeid', '') else ''
        module_name = self.get_module_name(module_path)
        
        # Obtener descripción del docstring si existe
        description = self.extract_test_description(test, test_name)
        
        # Resultado del test
        outcome = test.get('outcome', 'unknown')
        
        # Información de HTTP si está disponible
        expected_result = self.extract_expected_result(test, test_name)
        actual_result = self.extract_actual_result(test)
        
        # Duración real del test
        duration = test.get('call', {}).get('duration', 0)
        
        return {
            'name': test_name,
            'module': module_name,
            'description': description,
            'expected_result': expected_result,
            'actual_result': actual_result,
            'outcome': outcome,
            'duration': round(duration, 3)
        }

    def get_module_name(self, module_path):
        """Convierte la ruta del módulo a un nombre legible"""
        if 'auth' in module_path:
            return 'Autenticación'
        elif 'user' in module_path:
            return 'Usuarios'
        elif 'recipe' in module_path:
            return 'Recetas'
        else:
            return 'General'

    def extract_test_description(self, test, test_name):
        """Extrae la descripción del test desde el docstring"""
        # Mapeo de descripciones por nombre de test
        descriptions = {
            'test_root': 'Verificar que el endpoint raíz responda correctamente',
            'test_login_success': 'Verificar login exitoso con credenciales válidas',
            'test_login_invalid_credentials': 'Verificar login fallido con credenciales inválidas',
        }
        
        return descriptions.get(test_name, 'Test de funcionalidad')

    def extract_expected_result(self, test, test_name):
        """Extrae el resultado esperado basado en el nombre del test"""
        expected_results = {
            'test_root': 'Status Code: 200',
            'test_login_success': 'Status Code: 200, Token de acceso',
            'test_login_invalid_credentials': 'Status Code: 401, Error de credenciales',
        }
        
        return expected_results.get(test_name, 'Resultado exitoso')

    def extract_actual_result(self, test):
        """Extrae el resultado actual del test"""
        if test.get('outcome') == 'passed':
            return 'Test pasó correctamente'
        elif test.get('outcome') == 'failed':
            return f"Test falló: {test.get('call', {}).get('longrepr', 'Error no especificado')}"
        else:
            return 'Estado desconocido'

    def organize_tests_by_module(self):
        """Organiza los tests por módulo"""
        modules = {}
        
        for test in self.test_results.get('tests', []):
            test_info = self.parse_test_info(test)
            module_name = test_info['module']
            
            if module_name not in modules:
                modules[module_name] = []
            
            modules[module_name].append(test_info)
        
        return modules

    def create_test_table(self, tests):
        """Crea una tabla con los resultados de los tests"""
        # Encabezados de la tabla
        headers = [
            Paragraph('<b>Test</b>', self.styles['TableText']),
            Paragraph('<b>Descripción</b>', self.styles['TableText']),
            Paragraph('<b>Resultado Esperado</b>', self.styles['TableText']),
            Paragraph('<b>Resultado Obtenido</b>', self.styles['TableText']),
            Paragraph('<b>Estado</b>', self.styles['TableText']),
            Paragraph('<b>Duración(s)</b>', self.styles['TableText'])
        ]
        
        # Datos de la tabla
        data = [headers]
        
        for test in tests:
            status = '✓ PASS' if test['outcome'] == 'passed' else '✗ FAIL'
            status_color = '<font color="green">✓ PASS</font>' if test['outcome'] == 'passed' else '<font color="red">✗ FAIL</font>'
            
            # Usar Paragraph para permitir ajuste de texto
            data.append([
                Paragraph(test['name'], self.styles['TableText']),
                Paragraph(test['description'], self.styles['TableText']),
                Paragraph(test['expected_result'], self.styles['TableText']),
                Paragraph(test['actual_result'], self.styles['TableText']),
                Paragraph(status_color, self.styles['TableText']),
                Paragraph(str(test['duration']), self.styles['TableText'])
            ])
        
        # Crear tabla con anchos apropiados para orientación horizontal
        # Usando landscape, tenemos más espacio horizontal
        table = Table(data, colWidths=[
            1.8*inch,  # Test name
            3.2*inch,  # Description
            2.2*inch,  # Expected result
            2.2*inch,  # Actual result
            1.0*inch,  # Status
            0.8*inch   # Duration
        ])
        
        # Estilo de la tabla
        table.setStyle(TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Contenido
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            
            # Padding para mejor legibilidad
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        return table

    def create_summary_table(self, modules):
        """Crea una tabla resumen con estadísticas por módulo"""
        headers = ['Módulo', 'Tests Totales', 'Pasaron', 'Fallaron', 'Porcentaje Éxito']
        data = [headers]
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for module_name, tests in modules.items():
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
            'TOTAL',
            str(total_tests),
            str(total_passed),
            str(total_failed),
            f"{total_success_rate:.1f}%"
        ])
        
        # Crear tabla
        table = Table(data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
        
        # Estilo de la tabla
        table.setStyle(TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            # Contenido
            ('BACKGROUND', (0, 1), (-1, -2), colors.lightblue),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Fila de totales
            ('BACKGROUND', (0, -1), (-1, -1), colors.yellow),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        return table

    def generate_pdf_report(self, filename='test_report.pdf'):
        """Genera el PDF con los resultados de los tests"""
        from reportlab.lib.pagesizes import landscape
        
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
        
        # Título del documento
        title = Paragraph('Reporte de Tests - NutriPAE', self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Información general
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y %H:%M:%S")
        
        info_text = f"""
        <b>Fecha de Ejecución:</b> {date_str}<br/>
        <b>Proyecto:</b> NutriPAE - Sistema de Gestión Nutricional<br/>
        <b>Versión:</b> 1.0<br/>
        <b>Entorno:</b> Testing
        """
        
        info_para = Paragraph(info_text, self.styles['CustomNormal'])
        story.append(info_para)
        story.append(Spacer(1, 20))
        
        # Organizar tests por módulo
        modules = self.organize_tests_by_module()
        
        # Resumen ejecutivo
        story.append(Paragraph('Resumen Ejecutivo', self.styles['ModuleTitle']))
        story.append(Spacer(1, 10))
        
        summary_table = self.create_summary_table(modules)
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Cambiar a orientación horizontal para los detalles
        story.append(NextPageTemplate('landscape'))
        story.append(PageBreak())
        
        # Título para la sección de detalles
        title_details = Paragraph('Detalles por Módulo', self.styles['CustomTitle'])
        story.append(title_details)
        story.append(Spacer(1, 20))
        
        # Crear una página por módulo
        for i, (module_name, tests) in enumerate(modules.items()):
            if i > 0:  # Salto de página antes de cada módulo (excepto el primero)
                story.append(PageBreak())
            
            # Título del módulo
            module_title = Paragraph(f'Módulo: {module_name}', self.styles['ModuleTitle'])
            story.append(module_title)
            story.append(Spacer(1, 15))
            
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
            
            stats_para = Paragraph(stats_text, self.styles['Summary'])
            story.append(stats_para)
            story.append(Spacer(1, 15))
            
            # Tabla de tests del módulo
            module_table = self.create_test_table(tests)
            story.append(module_table)
            story.append(Spacer(1, 20))
        
        # Construir el PDF
        doc.build(story)
        print(f"Reporte PDF generado: {filename}")

def main():
    """Función principal"""
    print("=== Generador de Reportes de Tests NutriPAE ===")
    
    # Crear instancia del generador
    generator = TestReportGenerator()
    
    # Ejecutar tests y capturar resultados
    success = generator.run_tests_and_capture_results()
    
    # Generar PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reporte_tests_{timestamp}.pdf"
    generator.generate_pdf_report(filename)
    
    print(f"\n{'='*50}")
    print(f"Reporte generado exitosamente: {filename}")
    print(f"{'='*50}")
    
    # Limpiar archivos temporales
    if Path('test_results.json').exists():
        Path('test_results.json').unlink()

if __name__ == "__main__":
    main() 