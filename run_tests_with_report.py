#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

def main():
    print("Ejecutando tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            'poetry', 'run', 'python', 'generate_test_report.py'
        ], check=True)
        
        print("\n Tests ejecutados exitosamente!")
        
        pdf_files = list(Path('.').glob('reporte_tests_*.pdf'))
        if pdf_files:
            latest_pdf = max(pdf_files, key=lambda x: x.stat().st_mtime)
            print(f"Archivo generado: {latest_pdf}")
            
            try:
                subprocess.run(['xdg-open', str(latest_pdf)], check=False)
                print("Intentando abrir el PDF automáticamente...")
            except:
                print("Abre manualmente el archivo PDF generado")
        
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar los tests: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario")
        sys.exit(1)

if __name__ == "__main__":
    main() 