# NutriPAE - Sistema de Tests y Reportes

Sistema de tests automatizados para el proyecto NutriPAE con generación de reportes PDF formales.

## Características

- ✅ Ejecución automatizada de tests
- ✅ Generación de reportes PDF profesionales
- ✅ Organización por módulos (Autenticación, Usuarios, Recetas, etc.)
- ✅ Tablas detalladas con resultados de cada test
- ✅ Resumen ejecutivo con estadísticas
- ✅ Orientación horizontal para mejor legibilidad
- ✅ Timestamps automáticos
- ✅ Apertura automática del PDF generado

## Estructura del Proyecto

```
nutripae-tests/
├── tests/
│   ├── __init__.py
│   ├── config.py                    # Configuración y variables de entorno
│   └── auth/
│       ├── __init__.py
│       └── auth-test.py            # Tests de autenticación
├── generate_test_report.py         # Generador de reportes PDF
├── run_tests_with_report.py        # Script conveniente
├── pyproject.toml                  # Dependencias del proyecto
└── README.md                       # Este archivo
```

## Instalación

1. Instalar dependencias:
```bash
poetry install
```

2. Configurar variables de entorno:
```bash
# Crear archivo .env con las siguientes variables:
BASE_AUTH_BACKEND_URL=http://localhost:8000/api/v1
BASE_FRONTEND_URL=http://localhost:3000
ADMIN_USER_EMAIL=admin@example.com
ADMIN_USER_PASSWORD=admin123
BASE_USER_EMAIL=user@example.com
BASE_USER_PASSWORD=user123
```

## Uso

### Método 1: Script Conveniente (Recomendado)

```bash
poetry run python run_tests_with_report.py
```

Este script:
- Ejecuta todos los tests
- Genera automáticamente el reporte PDF
- Intenta abrir el PDF generado
- Limpia archivos temporales

### Método 2: Generador Manual

```bash
poetry run python generate_test_report.py
```

### Método 3: Solo Tests

```bash
poetry run pytest tests/auth/auth-test.py -v
```

## Estructura del Reporte PDF

El reporte PDF generado incluye:

### 1. Página Principal (Vertical)
- **Título**: Reporte de Tests - NutriPAE
- **Información General**: Fecha, proyecto, versión, entorno
- **Resumen Ejecutivo**: Tabla con estadísticas por módulo
  - Módulo
  - Tests totales
  - Tests que pasaron
  - Tests que fallaron
  - Porcentaje de éxito

### 2. Páginas de Detalle (Horizontal)
- Una página por módulo
- **Título del Módulo**: Ej. "Módulo: Autenticación"
- **Estadísticas del Módulo**: Resumen numérico
- **Tabla Detallada** con:
  - Nombre del test
  - Descripción
  - Resultado esperado (Status Code HTTP)
  - Resultado obtenido
  - Estado (✓ PASS / ✗ FAIL)
  - Duración en segundos

## Configuración de Tests

### Variables de Entorno

Los tests utilizan las siguientes variables de entorno (definidas en `tests/config.py`):

- `BASE_AUTH_BACKEND_URL`: URL del backend de autenticación
- `BASE_FRONTEND_URL`: URL del frontend
- `ADMIN_USER_EMAIL`: Email del usuario administrador
- `ADMIN_USER_PASSWORD`: Contraseña del usuario administrador
- `BASE_USER_EMAIL`: Email del usuario básico
- `BASE_USER_PASSWORD`: Contraseña del usuario básico

### Agregar Nuevos Tests

1. Crear un nuevo archivo en la carpeta correspondiente (ej. `tests/users/user-test.py`)
2. Agregar el archivo __init__.py en la carpeta si no existe
3. Implementar los tests usando pytest
4. Actualizar el generador de reportes para incluir el nuevo módulo

Ejemplo de test:

```python
import requests
import pytest
from ..config import settings

def test_user_creation():
    """Test para crear un usuario nuevo"""
    user_data = {
        "email": "test@example.com",
        "password": "test123"
    }
    
    response = requests.post(
        f"{settings.BASE_AUTH_BACKEND_URL}/users/", 
        json=user_data,
        timeout=5
    )
    
    assert response.status_code == 201
    assert "id" in response.json()
```

## Dependencias

- `pytest`: Framework de testing
- `requests`: Cliente HTTP para tests
- `pydantic`: Validación de configuración
- `pydantic-settings`: Manejo de variables de entorno
- `reportlab`: Generación de PDFs
- `pytest-json-report`: Exportación de resultados en JSON

## Archivos Generados

- `reporte_tests_YYYYMMDD_HHMMSS.pdf`: Reporte PDF principal
- `test_results.json`: Archivo temporal con resultados (se limpia automáticamente)

## Personalización

### Agregar Nuevos Módulos

1. Actualizar `get_module_name()` en `generate_test_report.py`
2. Agregar descripciones en `extract_test_description()`
3. Agregar resultados esperados en `extract_expected_result()`

### Modificar Estilos del PDF

Los estilos se pueden personalizar en `setup_custom_styles()` en `generate_test_report.py`.

## Solución de Problemas

### Tests se cuelgan
- Verificar que el backend esté ejecutándose
- Verificar las URLs en las variables de entorno
- Los tests tienen timeout de 5 segundos para evitar cuelgues

### Error de importación
- Verificar que existen los archivos `__init__.py` en las carpetas de tests
- Verificar que las rutas de importación son correctas

### PDF no se genera
- Verificar que reportlab esté instalado
- Verificar permisos de escritura en el directorio

## Comando Rápido

```bash
# Ejecutar tests y generar reporte en un solo comando
poetry run python run_tests_with_report.py
```

¡El PDF se abrirá automáticamente cuando esté listo!