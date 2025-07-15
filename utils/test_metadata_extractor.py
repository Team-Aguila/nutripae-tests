"""
Extractor de metadata de tests
"""
import importlib
import inspect
import json
import os


class MetadataError(Exception):
    """Excepción para errores de metadata de tests"""
    pass


_metadata_registry = None

def _load_metadata_registry():
    """Carga el registro de metadata desde el archivo JSON si aún no se ha cargado."""
    global _metadata_registry
    if _metadata_registry is None:
        _metadata_registry = {}
        registry_path = "test_metadata_registry.json"
        if os.path.exists(registry_path):
            try:
                with open(registry_path, "r") as f:
                    _metadata_registry = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Advertencia: No se pudo cargar el registro de metadata de tests: {e}")
    return _metadata_registry


def extract_test_metadata_from_source(module_path: str, function_name: str):
    """
    Extrae metadata desde el registro de metadata generado por pytest.
    
    Args:
        module_path: Ruta del módulo (ej: "tests/auth/auth-test.py")
        function_name: Nombre de la función de test
        
    Returns:
        Dict con metadata del test
        
    Raises:
        MetadataError: Si no se puede extraer metadata completa
    """
    registry = _load_metadata_registry()
    test_key = f"{module_path}::{function_name}"
    
    metadata = registry.get(test_key)
    
    if not metadata:
        # Fallback por si el registro no existe o está incompleto
        return _extract_from_docstring_fallback(module_path, function_name)

    # Validar que todos los campos obligatorios estén presentes
    missing_fields = [field for field in ['description', 'expected_result', 'module', 'test_id'] if not metadata.get(field)]
    
    if missing_fields:
        raise MetadataError(
            f"Test {function_name} en {module_path} tiene metadata incompleta en el registro. Campos faltantes: {', '.join(missing_fields)}."
        )
        
    return metadata


def _extract_from_docstring_fallback(module_path: str, function_name: str):
    """
    Fallback para extraer metadata del docstring si el registro no está disponible.
    """
    try:
        module_name = module_path.replace('/', '.').replace('-', '_').replace('.py', '')
        module = importlib.import_module(module_name)
        test_function = getattr(module, function_name, None)
        
        if not test_function or not inspect.getdoc(test_function):
            raise MetadataError(f"No se encontró docstring para {function_name} en {module_path}")

        docstring = inspect.getdoc(test_function)
        lines = docstring.strip().split('\n')
        metadata = {'description': lines[0].strip()}
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('Expected:'):
                metadata['expected_result'] = line.replace('Expected:', '').strip()
            elif line.startswith('Module:'):
                metadata['module'] = line.replace('Module:', '').strip()
            elif line.startswith('ID:'):
                metadata['test_id'] = line.replace('ID:', '').strip()

        missing_fields = [field for field in ['description', 'expected_result', 'module', 'test_id'] if not metadata.get(field)]
        if missing_fields:
            raise MetadataError(
                f"Test {function_name} en {module_path} no tiene los campos obligatorios en el docstring: {', '.join(missing_fields)}."
            )
        return metadata
    except Exception as e:
        raise MetadataError(
            f"Error al procesar test {function_name} en {module_path}. "
            f"Asegúrate de que el test tenga decorador @test_info o docstring estructurado "
            f"con todos los campos obligatorios: description, expected_result, module, test_id. Error: {e}"
        )


def get_module_name(module_path: str) -> str:
    """
    Convierte la ruta del módulo a un nombre legible
    
    Args:
        module_path: Ruta del archivo de test
        
    Returns:
        Nombre legible del módulo
    """
    module_path = module_path.lower()
    
    if 'auth' in module_path:
        return 'Autenticación'
    elif 'compras' in module_path:
        return 'Compras'
    elif 'menus' in module_path:
        return 'Menús'
    elif 'user' in module_path:
        return 'Usuarios'
    elif 'recipe' in module_path:
        return 'Recetas'
    else:
        return 'General'


def parse_test_info(test):
    """
    Extrae información detallada de un test desde los resultados de pytest
    
    Args:
        test: Resultado de test desde pytest JSON
        
    Returns:
        Dict con información procesada del test
        
    Raises:
        MetadataError: Si no se puede extraer metadata completa
    """
    # Extraer nombre del test
    test_name = test.get('nodeid', '').split('::')[-1] if '::' in test.get('nodeid', '') else test.get('nodeid', '')
    
    # Extraer módulo
    module_path = test.get('nodeid', '').split('::')[0] if '::' in test.get('nodeid', '') else ''
    
    if not test_name:
        raise MetadataError(f"No se pudo extraer nombre del test de: {test.get('nodeid', 'nodeid desconocido')}")
    
    if not module_path:
        raise MetadataError(f"No se pudo extraer ruta del módulo de: {test.get('nodeid', 'nodeid desconocido')}")
    
    # Extraer metadata del código fuente (obligatorio)
    try:
        source_metadata = extract_test_metadata_from_source(module_path, test_name)
    except MetadataError:
        # Re-lanzar la excepción con contexto adicional
        raise MetadataError(
            f"Error al procesar test {test_name} en {module_path}. "
            f"Asegúrate de que el test tenga decorador @test_info o docstring estructurado "
            f"con todos los campos obligatorios: description, expected_result, module, test_id"
        )
    
    # Usar metadata del código fuente
    description = source_metadata['description']
    expected_result = source_metadata['expected_result']
    module_name = source_metadata['module']
    test_id = source_metadata['test_id']
    
    # Resultado del test
    outcome = test.get('outcome', 'unknown')
    
    # Resultado actual del test
    actual_result = extract_actual_result(test)
    
    # Duración real del test
    duration = test.get('call', {}).get('duration', 0)
    
    return {
        'name': test_name,
        'module': module_name,
        'description': description,
        'expected_result': expected_result,
        'actual_result': actual_result,
        'outcome': outcome,
        'duration': round(duration, 3),
        'test_id': test_id
    }


def extract_actual_result(test):
    """
    Extrae el resultado actual del test
    
    Args:
        test: Resultado de test desde pytest JSON
        
    Returns:
        Descripción del resultado obtenido
    """
    if test.get('outcome') == 'passed':
        return 'Test pasó correctamente'
    elif test.get('outcome') == 'failed':
        longrepr = test.get('call', {}).get('longrepr', 'Error no especificado')
        # Truncar mensajes muy largos
        if len(longrepr) > 100:
            longrepr = longrepr[:100] + "..."
        return f"Test falló: {longrepr}"
    elif test.get('outcome') == 'skipped':
        return 'Test fue omitido'
    else:
        return 'Estado desconocido'


def validate_all_tests_have_metadata(test_results):
    """
    Valida que todos los tests tengan metadata completa
    
    Args:
        test_results: Resultados de pytest JSON
        
    Raises:
        MetadataError: Si algún test no tiene metadata completa
    """
    missing_metadata_tests = []
    
    for test in test_results.get('tests', []):
        test_name = test.get('nodeid', '').split('::')[-1] if '::' in test.get('nodeid', '') else test.get('nodeid', '')
        module_path = test.get('nodeid', '').split('::')[0] if '::' in test.get('nodeid', '') else ''
        
        try:
            parse_test_info(test)
        except MetadataError as e:
            missing_metadata_tests.append(f"{test_name} ({module_path}): {str(e)}")
    
    if missing_metadata_tests:
        error_msg = "Los siguientes tests no tienen metadata completa:\n\n"
        error_msg += "\n".join(f"• {test}" for test in missing_metadata_tests)
        error_msg += "\n\nPor favor, agrega @test_info o docstring estructurado a todos los tests."
        raise MetadataError(error_msg) 