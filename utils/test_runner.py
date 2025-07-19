"""
Ejecutor de tests para todos los servicios
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, Any
from .test_metadata_extractor import MetadataError, validate_all_tests_have_metadata


def run_all_tests():
    """
    Ejecuta todos los tests de todos los servicios y captura los resultados

    Returns:
        Dict con los resultados de pytest JSON

    Raises:
        TestMetadataError: Si algún test no tiene metadata completa
        RuntimeError: Si hay errores al ejecutar pytest
    """
    print("Ejecutando tests de todos los servicios...")
    print("=" * 50)

    # Ejecutar tests de todos los servicios
    test_paths = [
        "tests/auth/",
        'tests/cobertura/',
        "tests/compras/",
        "tests/menus/",
        "tests/ui/menus",
        "tests/ui/rh",
        "tests/rh"
        'tests/ui/cobertura-ui'

    ]

    # Filtrar solo las rutas que existen
    existing_paths = []
    for path in test_paths:
        if Path(path).exists():
            existing_paths.append(path)
            print(f"✓ Encontrado: {path}")
        else:
            print(f"⚠ No encontrado: {path}")

    if not existing_paths:
        raise RuntimeError("No se encontraron directorios de tests")

    print(f"\nEjecutando pytest en: {', '.join(existing_paths)}")
    print("-" * 50)

    # Ejecutar tests con reporte JSON
    cmd = (
        ["poetry", "run", "pytest"]
        + existing_paths
        + ["--json-report", "--json-report-file=test_results.json", "-v", "--tb=short"]
    )

    result = subprocess.run(cmd, capture_output=True, text=True)

    print("Salida de pytest:")
    print(result.stdout)
    if result.stderr:
        print("Errores/Advertencias:")
        print(result.stderr)

    # Cargar resultados JSON
    try:
        with open("test_results.json", "r") as f:
            test_results = json.load(f)
    except FileNotFoundError:
        raise RuntimeError("Error: No se pudo generar el archivo de resultados JSON")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error al parsear JSON de resultados: {e}")

    # Validar que todos los tests tengan metadata completa
    print("\n" + "=" * 50)
    print("Validando metadata de tests...")
    try:
        validate_all_tests_have_metadata(test_results)
        print("✓ Todos los tests tienen metadata completa")
    except MetadataError as e:
        print("✗ Error de metadata:")
        print(str(e))
        raise

    # Estadísticas rápidas
    total_tests = len(test_results.get("tests", []))
    passed_tests = sum(
        1 for test in test_results.get("tests", []) if test.get("outcome") == "passed"
    )
    failed_tests = sum(
        1 for test in test_results.get("tests", []) if test.get("outcome") == "failed"
    )
    skipped_tests = sum(
        1 for test in test_results.get("tests", []) if test.get("outcome") == "skipped"
    )

    print(f"\n📊 Resumen rápido:")
    print(f"   Total: {total_tests}")
    print(f"   Pasaron: {passed_tests}")
    print(f"   Fallaron: {failed_tests}")
    print(f"   Omitidos: {skipped_tests}")

    if failed_tests > 0:
        print(
            f"\n⚠ Hay {failed_tests} tests fallidos, pero el reporte se generará de todas formas"
        )

    return test_results


def organize_tests_by_module(test_results: Dict[str, Any]) -> Dict[str, list]:
    """
    Organiza los tests por módulo en orden alfabético

    Args:
        test_results: Resultados de pytest JSON

    Returns:
        Dict con tests organizados por módulo
    """
    from .test_metadata_extractor import parse_test_info

    modules = {}

    for test in test_results.get("tests", []):
        try:
            test_info = parse_test_info(test)
            module_name = test_info["module"]

            if module_name not in modules:
                modules[module_name] = []

            modules[module_name].append(test_info)
        except MetadataError as e:
            print(f"Error procesando test: {e}")
            raise

    # Ordenar alfabéticamente por módulo
    sorted_modules = {}
    for module_name in sorted(modules.keys()):
        # También ordenar tests dentro de cada módulo
        sorted_modules[module_name] = sorted(
            modules[module_name], key=lambda x: x["name"]
        )

    return sorted_modules


def cleanup_temp_files():
    """Limpia archivos temporales generados por pytest"""
    temp_files = ["test_results.json", ".pytest_cache"]

    for file_path in temp_files:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                path.unlink()
                print(f"✓ Limpiado: {file_path}")
            elif path.is_dir():
                import shutil

                shutil.rmtree(path)
                print(f"✓ Limpiado directorio: {file_path}")

    print("Archivos temporales limpiados.")
