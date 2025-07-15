#!/usr/bin/env python3
"""
Generador de reportes PDF para los tests de NutriPAE
Archivo principal único para ejecutar tests y generar reportes
"""
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Importar utilidades propias
from utils.test_runner import run_all_tests, organize_tests_by_module, cleanup_temp_files
from utils.pdf_generator import generate_pdf_report
from utils.test_metadata_extractor import MetadataError


def main():
    """Función principal del generador de reportes"""
    print("=== Generador de Reportes de Tests NutriPAE ===")
    print("Ejecutando tests de todos los servicios: Auth, Compras, Menús")
    print("Generando reporte PDF con metadata dinámica")
    print()
    
    try:
        # 1. Ejecutar todos los tests y validar metadata
        print("PASO 1: Ejecutando tests...")
        test_results = run_all_tests()
        
        # 2. Organizar tests por módulo (orden alfabético)
        print("\nPASO 2: Organizando tests por módulo...")
        modules = organize_tests_by_module(test_results)
        
        print(f"Módulos encontrados: {list(modules.keys())}")
        for module_name, tests in modules.items():
            print(f"   • {module_name}: {len(tests)} tests")
        
        # 3. Generar PDF
        print("\nPASO 3: Generando PDF...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_tests_nutripae_{timestamp}.pdf"
        
        generate_pdf_report(modules, filename)
        
        # 4. Mostrar resumen final
        print("\n" + "="*60)
        print("REPORTE GENERADO EXITOSAMENTE")
        print("="*60)
        print(f"Archivo: {filename}")
        print(f"Módulos incluidos: {len(modules)}")
        
        total_tests = sum(len(tests) for tests in modules.values())
        total_passed = sum(1 for tests in modules.values() for test in tests if test['outcome'] == 'passed')
        total_failed = sum(1 for tests in modules.values() for test in tests if test['outcome'] == 'failed')
        
        print(f"Total de tests: {total_tests}")
        print(f"Pasaron: {total_passed}")
        print(f"Fallaron: {total_failed}")
        print(f"Porcentaje de éxito: {(total_passed/total_tests)*100:.1f}%")
        
        print("\nCaracterísticas del reporte:")
        print("   • Metadata extraída dinámicamente del código")
        print("   • Resumen ejecutivo en primera página")
        print("   • Detalles por módulo en orden alfabético")
        print("   • Una página por módulo con salto de página")
        print("   • Tablas con información completa de cada test")
        
        print("\nEstructura del PDF:")
        print("   Página 1: Resumen ejecutivo (todos los servicios)")
        for i, module_name in enumerate(modules.keys(), 2):
            print(f"   Página {i}: Módulo {module_name}")
            
        print("="*60)
        
        # 5. Intentar abrir el PDF automáticamente
        print("\nIntentando abrir el PDF automáticamente...")
        try:
            subprocess.run(['xdg-open', str(filename)], check=False)
            print("PDF abierto (si tienes un visor PDF instalado)")
        except Exception as e:
            print(f"No se pudo abrir automáticamente: {e}")
            print(f"Abre manually el archivo: {filename}")
        
    except MetadataError as e:
        print("\nERROR DE METADATA:")
        print(str(e))
        print("\nSolución:")
        print("   Agrega @test_info o docstring estructurado a todos los tests")
        print("   Ejemplo usando decorador:")
        print("   @test_info(")
        print("       description='Descripción del test',")
        print("       expected_result='Status Code: 200',")
        print("       module='Nombre del módulo',")
        print("       test_id='ID-001'")
        print("   )")
        print("\n   Ejemplo usando docstring:")
        print("   def test_ejemplo():")
        print("       '''")
        print("       Descripción del test")
        print("       Expected: Status Code: 200")
        print("       Module: Nombre del módulo")
        print("       ID: ID-001")
        print("       '''")
        sys.exit(1)
        
    except Exception as e:
        print(f"\nERROR INESPERADO: {e}")
        sys.exit(1)
        
    finally:
        # Limpiar archivos temporales
        print("\nLimpiando archivos temporales...")
        cleanup_temp_files()


if __name__ == "__main__":
    main() 