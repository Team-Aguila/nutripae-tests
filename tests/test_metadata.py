"""
Módulo para decoradores y metadata de tests personalizados
"""
import functools
import inspect
from typing import Dict, Any, Optional, Callable
import os


def add_test_info(description: str, expected_result: str, module: str = None, test_id: str = None):
    """
    Decorador para agregar metadata a los tests
    
    Args:
        description: Descripción detallada del test
        expected_result: Resultado esperado del test
        module: Módulo al que pertenece (opcional)
        test_id: ID único del test (opcional)
    """
    def decorator(func: Callable) -> Callable:
        # Agregar metadata como atributos de la función
        func._test_description = description
        func._test_expected_result = expected_result
        func._test_module = module
        func._test_id = test_id

        # Crear el wrapper apropiado para funciones sync y async
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        # Copiar los atributos al wrapper para que sean accesibles
        wrapper._test_description = description
        wrapper._test_expected_result = expected_result
        wrapper._test_module = module
        wrapper._test_id = test_id
        
        # Registrar metadata en el registry
        try:
            registry = MetadataRegistry()
            module_path = os.path.relpath(inspect.getfile(func))
            test_key = f"{module_path}::{func.__name__}"
            
            metadata = {
                'description': description,
                'expected_result': expected_result,
                'module': module,
                'test_id': test_id
            }
            registry.register_test(test_key, metadata)
        except Exception:
            # No fallar si el registro falla
            pass

        return wrapper
    return decorator


def extract_test_metadata(func: Callable) -> Dict[str, Any]:
    """
    Extrae metadata de una función de test
    
    Args:
        func: Función de test
        
    Returns:
        Dict con la metadata del test
    """
    metadata = {}
    
    # Extraer del decorador @add_test_info
    metadata['description'] = getattr(func, '_test_description', None)
    metadata['expected_result'] = getattr(func, '_test_expected_result', None)
    metadata['module'] = getattr(func, '_test_module', None)
    metadata['test_id'] = getattr(func, '_test_id', None)
    
    # Extraer del docstring si no hay decorador
    if not metadata['description']:
        docstring = inspect.getdoc(func)
        if docstring:
            # Parsear docstring estructurado
            lines = docstring.strip().split('\n')
            if lines:
                # Primera línea como descripción principal
                metadata['description'] = lines[0].strip()
                
                # Buscar metadata adicional en el docstring
                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith('Expected:'):
                        metadata['expected_result'] = line.replace('Expected:', '').strip()
                    elif line.startswith('Module:'):
                        metadata['module'] = line.replace('Module:', '').strip()
                    elif line.startswith('ID:'):
                        metadata['test_id'] = line.replace('ID:', '').strip()
    
    # Valores por defecto
    if not metadata['description']:
        metadata['description'] = func.__name__.replace('_', ' ').title()
    if not metadata['expected_result']:
        metadata['expected_result'] = 'Test debe pasar exitosamente'
    
    return metadata


def get_test_function_by_name(module_path: str, function_name: str) -> Optional[Callable]:
    """
    Obtiene una función de test por su nombre y ruta del módulo
    
    Args:
        module_path: Ruta del módulo (ej: "tests.auth.auth_test")
        function_name: Nombre de la función
        
    Returns:
        Función si se encuentra, None en caso contrario
    """
    try:
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, function_name, None)
    except (ImportError, AttributeError):
        return None


class MetadataRegistry:
    """Registry para almacenar metadata de tests"""
    
    _instance = None
    _tests = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetadataRegistry, cls).__new__(cls)
        return cls._instance
    
    def register_test(self, test_name: str, metadata: Dict[str, Any]):
        """Registrar metadata de un test"""
        self._tests[test_name] = metadata
    
    def get_test_metadata(self, test_name: str) -> Dict[str, Any]:
        """Obtener metadata de un test"""
        return self._tests.get(test_name, {})
    
    def get_all_tests(self) -> Dict[str, Dict[str, Any]]:
        """Obtener metadata de todos los tests"""
        return self._tests.copy() 