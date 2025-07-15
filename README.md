# NutriPAE - Sistema de Tests y Reportes

Sistema de tests automatizados para el proyecto NutriPAE con generación de reportes PDF. Ejecuta tests de todos los servicios (Autenticación, Compras, Menús) y genera un reporte profesional con metadata extraída dinámicamente del código fuente.

## Características

- Ejecución automatizada de tests de todos los servicios
- Generación de reportes PDF profesionales con orientación horizontal
- Extracción dinámica de metadata desde el código fuente
- Organización por módulos en orden alfabético
- Resumen ejecutivo con estadísticas generales
- Páginas detalladas por módulo con salto de página automático
- Validación obligatoria de metadata completa
- Apertura automática del PDF generado

## Estructura del Proyecto

```
nutripae-tests/
├── utils/                           # Utilidades modulares
│   ├── __init__.py
│   ├── pdf_generator.py            # Generador de PDF
│   ├── pdf_styles.py               # Estilos del PDF
│   ├── pdf_tables.py               # Tablas del PDF
│   ├── test_metadata_extractor.py  # Extractor de metadata
│   └── test_runner.py              # Ejecutor de tests
├── tests/                           # Tests organizados por servicio
│   ├── __init__.py
│   ├── config.py                    # Configuración y variables
│   ├── test_metadata.py             # Decoradores para metadata
│   ├── auth/                        # Tests de autenticación
│   ├── compras/                     # Tests de compras
│   └── menus/                       # Tests de menús
├── generate_test_report.py         # Archivo principal único
├── pyproject.toml                  # Dependencias y comandos
└── README.md                       # Este archivo
```

## Instalación

1. Instalar dependencias:
```bash
poetry install
```

2. Configurar variables de entorno.

## Uso

El sistema provee múltiples comandos para ejecutar los tests:

### Comandos de Poetry (Recomendado)

```bash
poetry run nutripae-tests
```

### Comando Manual

```bash
poetry run python generate_test_report.py
```

### Solo Tests (sin reporte)

```bash
poetry run pytest tests/ -v
```

## Metadata Obligatoria para Tests

Todos los tests deben incluir metadata completa usando uno de estos métodos:

### Método 1: Decorador @test_info

```python
from tests.test_metadata import test_info

@test_info(
    description="Verificar login exitoso con credenciales válidas",
    expected_result="Status Code: 200, Access Token, Token Type Bearer",
    module="Autenticación",
    test_id="AUTH-002"
)
def test_login_success():
    # Código del test
    pass
```

### Método 2: Docstring Estructurado

```python
def test_password_reset_request():
    """
    Test para solicitar restablecimiento de contraseña
    
    Verifica que el sistema permita solicitar el restablecimiento
    de contraseña enviando un email válido.
    
    Expected: HTTP 200, mensaje confirmando envío de email
    Module: Autenticación
    ID: AUTH-004
    """
    # Código del test
    pass
```

### Campos Obligatorios

- **description**: Descripción detallada del test
- **expected_result**: Resultado esperado (ej. "Status Code: 200")
- **module**: Módulo al que pertenece (ej. "Autenticación")
- **test_id**: ID único del test (ej. "AUTH-001")

## Estructura del Reporte PDF

### Página 1: Resumen Ejecutivo
- Información general del proyecto
- Tabla resumen con estadísticas por módulo
- Totales generales de todos los servicios

### Páginas Siguientes: Detalles por Módulo
- Una página por módulo en orden alfabético
- Salto de página automático entre módulos
- Estadísticas específicas del módulo
- Tabla detallada con información completa:
  - ID del test
  - Nombre del test
  - Descripción
  - Resultado esperado
  - Resultado obtenido
  - Estado (PASS/FAIL)
  - Duración en segundos

## Servicios Incluidos

### Autenticación
- Tests de login y logout
- Validación de credenciales
- Manejo de tokens

### Compras
- Tests de productos y proveedores
- Gestión de inventario
- Órdenes de compra

### Menús
- Tests de ingredientes y platos
- Ciclos de menús
- Programación de menús

## Configuración de Tests

### Variables de Entorno por Servicio

**Autenticación:**
- `BASE_AUTH_BACKEND_URL`: URL del backend de autenticación
- `ADMIN_USER_EMAIL`: Email del usuario administrador
- `ADMIN_USER_PASSWORD`: Contraseña del usuario administrador

**Compras:**
- `PAE_COMPRAS_BASE_URL`: URL del servicio de compras

**Menús:**
- `PAE_MENUS_BASE_URL`: URL del servicio de menús

### Agregar Nuevos Tests

1. Crear el archivo de test en la carpeta correspondiente
2. Agregar metadata obligatoria usando @test_info o docstring
3. Implementar el test usando pytest
4. El sistema detectará automáticamente el nuevo módulo

### Agregar Nuevos Servicios

1. Crear carpeta en `tests/`
2. Actualizar `get_module_name()` en `utils/test_metadata_extractor.py`
3. Agregar la ruta en `run_all_tests()` en `utils/test_runner.py`

## Dependencias

- `pytest`: Framework de testing
- `requests`: Cliente HTTP para tests
- `httpx`: Cliente HTTP asíncrono
- `pydantic`: Validación de configuración
- `reportlab`: Generación de PDFs
- `pytest-json-report`: Exportación de resultados
- `pytest-asyncio`: Soporte para tests asíncronos

## Archivos Generados

- `reporte_tests_nutripae_YYYYMMDD_HHMMSS.pdf`: Reporte PDF principal
- `test_results.json`: Archivo temporal (se limpia automáticamente)

## Solución de Problemas

### Error de Metadata Faltante
```
ERROR DE METADATA: Test no tiene los campos obligatorios
```
**Solución**: Agregar @test_info o docstring estructurado con todos los campos obligatorios

### Tests se Cuelgan
**Causa**: Backend no disponible
**Solución**: Verificar que los servicios estén ejecutándose y las URLs sean correctas

### PDF no se Genera
**Causa**: Permisos o dependencias
**Solución**: Verificar instalación de reportlab y permisos de escritura

### Error de Importación
**Causa**: Archivos __init__.py faltantes
**Solución**: Verificar que existan archivos __init__.py en todas las carpetas de tests

## Personalización

### Modificar Estilos del PDF
Editar `utils/pdf_styles.py` para cambiar colores, fuentes y espaciado.

### Cambiar Estructura de Tablas
Modificar `utils/pdf_tables.py` para ajustar columnas y contenido.

### Agregar Nuevos Módulos
Actualizar `utils/test_metadata_extractor.py` para reconocer nuevos tipos de módulos.

## Comandos Útiles

```bash
# Generar reporte completo
poetry run test-report

# Solo ejecutar tests
poetry run pytest tests/ -v

# Ejecutar tests de un servicio específico
poetry run pytest tests/auth/ -v

# Ver ayuda de pytest
poetry run pytest --help
```

El sistema ejecutará automáticamente los tests, validará la metadata, generará el PDF y intentará abrirlo. Los archivos temporales se limpian automáticamente al finalizar.